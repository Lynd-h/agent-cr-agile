import argparse
from pathlib import Path

import yaml

from llm import appeler_llm
from masquage import Masqueur
from skill import charger_prompt_skill, construire_demande
from verification import verifier_citations, verifier_format

RACINE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description="Génère le compte-rendu d'une transcription.")
    parser.add_argument("transcription", help="Chemin du fichier de transcription (.txt)")
    parser.add_argument("--modele", default=None, help="Nom du modèle défini dans le fichier de configuration (par défaut : le premier modèle actif)")
    parser.add_argument("--config", default="config.yaml", help="Fichier de configuration (config.yaml ou config_local.yaml)")
    args = parser.parse_args()

    config = yaml.safe_load((RACINE / args.config).read_text(encoding="utf-8"))
    if args.modele is None:
        modele = next((m for m in config["modeles_evalues"] if m.get("actif", True)), None)
    else:
        modele = next((m for m in config["modeles_evalues"] if m["nom"] == args.modele), None)
    if modele is None:
        noms = ", ".join(m["nom"] for m in config["modeles_evalues"])
        raise SystemExit(f"Modèle introuvable dans {args.config} : {args.modele}. Modèles disponibles : {noms}")

    chemin = Path(args.transcription)
    sensibles = config.get("donnees_sensibles", {})
    masqueur = Masqueur(sensibles.get("personnes"), sensibles.get("clients"))
    transcription_masquee = masqueur.masquer(chemin.read_text(encoding="utf-8"))
    print(f"Données masquées avant envoi : {masqueur.resume()}")

    parametres = config.get("parametres_generation", {})
    compte_rendu_masque = appeler_llm(
        modele,
        charger_prompt_skill(RACINE / "skill" / "compte-rendu-agile"),
        construire_demande(transcription_masquee),
        temperature=parametres.get("temperature"),
        max_tokens=parametres.get("max_tokens", 2000),
    )

    citations = verifier_citations(compte_rendu_masque, transcription_masquee)
    format_cr = verifier_format(compte_rendu_masque)
    compte_rendu = masqueur.demasquer(compte_rendu_masque)

    dossier = RACINE / "resultats" / "generations"
    dossier.mkdir(parents=True, exist_ok=True)
    sortie = dossier / f"{chemin.stem}_{modele['nom']}.md"
    sortie.write_text(compte_rendu, encoding="utf-8")

    print(compte_rendu)
    print("\n---")
    print(f"Sections présentes : {format_cr['sections_presentes']}/6")
    print(f"Citations vérifiées : {citations['taux_citations_exactes']} ({citations['nb_citations']} citations)")
    for citation in citations["citations_introuvables"]:
        print(f"  Citation introuvable dans la transcription : « {citation} »")
    print(f"Compte-rendu enregistré dans {sortie}")


if __name__ == "__main__":
    main()
