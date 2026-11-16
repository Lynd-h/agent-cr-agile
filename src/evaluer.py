import argparse
import json
import time
from pathlib import Path

import pandas as pd
import yaml

from juge import CRITERES, juger
from llm import appeler_llm
from masquage import Masqueur
from skill import charger_prompt_skill, construire_demande
from verification import detecter_fuites, verifier_citations, verifier_format

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_RESULTATS = RACINE / "resultats"


def lire_arguments():
    parser = argparse.ArgumentParser(description="Évalue plusieurs LLM sur les transcriptions pièges.")
    parser.add_argument("--config", default="config.yaml", help="Fichier de configuration (config.yaml ou config_local.yaml)")
    parser.add_argument("--sortie", default="resultats", help="Dossier où enregistrer les résultats")
    parser.add_argument("--modeles", nargs="*", help="Noms des modèles à évaluer (par défaut : tous les modèles actifs)")
    parser.add_argument("--transcriptions", nargs="*", help="Début des noms de fichiers à évaluer, par exemple 03 06")
    parser.add_argument("--sans-juge", action="store_true", help="Ne lance pas le LLM-juge (vérifications automatiques seulement)")
    parser.add_argument("--reprendre", action="store_true", help="Réutilise les comptes-rendus déjà générés dans le dossier de sortie")
    return parser.parse_args()


def charger_config(nom_fichier):
    return yaml.safe_load((RACINE / nom_fichier).read_text(encoding="utf-8"))


def choisir_modeles(config, noms):
    modeles = [m for m in config["modeles_evalues"] if m.get("actif", True)]
    if noms:
        modeles = [m for m in config["modeles_evalues"] if m["nom"] in noms]
    return modeles


def choisir_transcriptions(prefixes):
    fichiers = sorted((RACINE / "data" / "transcriptions").glob("*.txt"))
    if prefixes:
        fichiers = [f for f in fichiers if any(f.stem.startswith(p) for p in prefixes)]
    return fichiers


def masquer_attendu(attendu, masqueur):
    return {
        **attendu,
        "piege": masqueur.masquer(attendu["piege"]),
        "doit_contenir": [masqueur.masquer(e) for e in attendu["doit_contenir"]],
        "ne_doit_pas_contenir": [masqueur.masquer(e) for e in attendu["ne_doit_pas_contenir"]],
    }


def evaluer_une_sortie(identifiant, attendu, modele, compte_rendu, transcription, config, avec_juge):
    ligne = {"transcription": identifiant, "piege": attendu["piege_court"], "modele": modele["nom"]}
    ligne.update(verifier_format(compte_rendu))
    citations = verifier_citations(compte_rendu, transcription)
    ligne["nb_citations"] = citations["nb_citations"]
    ligne["taux_citations_exactes"] = citations["taux_citations_exactes"]
    ligne["citations_introuvables"] = " | ".join(citations["citations_introuvables"])
    if avec_juge:
        notes, justifications = juger(config["juge"], transcription, attendu, compte_rendu)
        for critere in CRITERES:
            ligne[critere] = notes[critere]
        ligne["note_globale"] = round(sum(notes.values()) / len(CRITERES), 2)
        for critere in CRITERES:
            ligne[f"justification_{critere}"] = justifications[critere]
    return ligne


def tableau_markdown(df):
    colonnes = [str(c) for c in df.columns]
    lignes = ["| " + " | ".join(colonnes) + " |", "|" + "---|" * len(colonnes)]
    for _, rangee in df.iterrows():
        valeurs = ["" if pd.isna(v) else (f"{v:.2f}" if isinstance(v, float) else str(v)) for v in rangee]
        lignes.append("| " + " | ".join(valeurs) + " |")
    return "\n".join(lignes)


def ecrire_synthese(df, chemin):
    colonnes = [c for c in CRITERES + ["note_globale", "taux_format", "taux_citations_exactes"] if c in df.columns]
    moyennes = df.groupby("modele")[colonnes].mean(numeric_only=True).reset_index()
    if "note_globale" in moyennes.columns:
        moyennes = moyennes.sort_values("note_globale", ascending=False)
    indicateur = "note_globale" if "note_globale" in df.columns else "taux_citations_exactes"
    par_piege = df.pivot_table(index="piege", columns="modele", values=indicateur, aggfunc="mean").reset_index()
    contenu = [
        "# Synthèse de l'évaluation",
        "",
        "## Moyennes par modèle",
        "",
        tableau_markdown(moyennes.round(2)),
        "",
        f"## {indicateur} par piège",
        "",
        tableau_markdown(par_piege.round(2)),
        "",
    ]
    chemin.write_text("\n".join(contenu), encoding="utf-8")


def main():
    global DOSSIER_RESULTATS
    args = lire_arguments()
    config = charger_config(args.config)
    DOSSIER_RESULTATS = RACINE / args.sortie
    prompt_systeme = charger_prompt_skill(RACINE / "skill" / "compte-rendu-agile")
    modeles = choisir_modeles(config, args.modeles)
    fichiers = choisir_transcriptions(args.transcriptions)
    parametres = config.get("parametres_generation", {})
    sensibles = config.get("donnees_sensibles", {})

    if not modeles or not fichiers:
        print("Aucun modèle actif ou aucune transcription trouvée.")
        return

    cas = []
    dossier_masque = DOSSIER_RESULTATS / "transcriptions_masquees"
    dossier_masque.mkdir(parents=True, exist_ok=True)
    for fichier in fichiers:
        identifiant = fichier.stem
        attendu = json.loads((RACINE / "data" / "attendus" / f"{identifiant}.json").read_text(encoding="utf-8"))
        masqueur = Masqueur(sensibles.get("personnes"), sensibles.get("clients"))
        transcription = masqueur.masquer(fichier.read_text(encoding="utf-8"))
        attendu = masquer_attendu(attendu, masqueur)
        fuites = detecter_fuites(transcription, masqueur)
        if fuites:
            print(f"ATTENTION : masquage incomplet pour {identifiant} : {fuites}")
            continue
        (dossier_masque / f"{identifiant}.txt").write_text(transcription, encoding="utf-8")
        cas.append((identifiant, transcription, attendu))

    total = len(cas) * len(modeles)
    print(f"\nPhase 1 : génération de {total} comptes-rendus, un modèle après l'autre")
    produits = []
    numero = 0
    for modele in modeles:
        dossier_cr = DOSSIER_RESULTATS / "comptes_rendus" / modele["nom"]
        dossier_cr.mkdir(parents=True, exist_ok=True)
        for identifiant, transcription, attendu in cas:
            numero += 1
            chemin_cr = dossier_cr / f"{identifiant}.md"
            if args.reprendre and chemin_cr.exists():
                print(f"  [{numero}/{total}] {modele['nom']} / {identifiant} : déjà fait, repris")
                produits.append((identifiant, transcription, attendu, modele, chemin_cr.read_text(encoding="utf-8")))
                continue
            debut = time.time()
            try:
                compte_rendu = appeler_llm(
                    modele,
                    prompt_systeme,
                    construire_demande(transcription),
                    temperature=parametres.get("temperature"),
                    max_tokens=parametres.get("max_tokens", 2000),
                )
            except Exception as erreur:
                print(f"  [{numero}/{total}] {modele['nom']} / {identifiant} : erreur de génération : {erreur}")
                continue
            chemin_cr.write_text(compte_rendu, encoding="utf-8")
            produits.append((identifiant, transcription, attendu, modele, compte_rendu))
            print(f"  [{numero}/{total}] {modele['nom']} / {identifiant} : fait en {time.time() - debut:.0f} s")

    avec_juge = not args.sans_juge
    print(f"\nPhase 2 : {'vérifications et notation par le juge' if avec_juge else 'vérifications automatiques'}")
    lignes = []
    for numero, (identifiant, transcription, attendu, modele, compte_rendu) in enumerate(produits, start=1):
        debut = time.time()
        try:
            ligne = evaluer_une_sortie(identifiant, attendu, modele, compte_rendu, transcription, config, avec_juge)
        except Exception as erreur:
            print(f"  [{numero}/{len(produits)}] {modele['nom']} / {identifiant} : erreur d'évaluation : {erreur}")
            continue
        lignes.append(ligne)
        resume = ligne.get("note_globale", ligne["taux_citations_exactes"])
        print(f"  [{numero}/{len(produits)}] {modele['nom']} / {identifiant} : {resume} ({time.time() - debut:.0f} s)")

    if not lignes:
        print("Aucun résultat.")
        return

    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(lignes)
    df.to_csv(DOSSIER_RESULTATS / "scores.csv", index=False, sep=";", encoding="utf-8-sig")
    ecrire_synthese(df, DOSSIER_RESULTATS / "synthese.md")
    print(f"\nRésultats : {DOSSIER_RESULTATS / 'scores.csv'} et {DOSSIER_RESULTATS / 'synthese.md'}")


if __name__ == "__main__":
    main()
