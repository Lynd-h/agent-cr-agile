import argparse
import importlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OK = "[OK]"
KO = "[PROBLÈME]"


def verifier_python():
    version = sys.version_info
    bon = version >= (3, 10)
    print(f"{OK if bon else KO} Python {version.major}.{version.minor}" + ("" if bon else " : installe Python 3.10 ou plus récent"))
    return bon


def verifier_paquets():
    tout_va_bien = True
    for paquet in ["anthropic", "openai", "yaml", "pandas", "pytest"]:
        try:
            importlib.import_module(paquet)
            print(f"{OK} paquet {paquet}")
        except ImportError:
            print(f"{KO} paquet {paquet} manquant : lance pip install -r requirements.txt")
            tout_va_bien = False
    return tout_va_bien


def modeles_ollama(base_url):
    adresse = base_url.rstrip("/").removesuffix("/v1") + "/api/tags"
    with urllib.request.urlopen(adresse, timeout=5) as reponse:
        donnees = json.loads(reponse.read().decode("utf-8"))
    return {m["name"] for m in donnees.get("models", [])}


def modele_installe(nom, installes):
    return nom in installes or f"{nom}:latest" in installes


def verifier_modele(config_modele, cache_ollama):
    from llm import appeler_llm

    nom = config_modele["nom"]
    if config_modele["fournisseur"] == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{KO} {nom} : variable ANTHROPIC_API_KEY absente")
        return False
    cle_env = config_modele.get("cle_env", "OPENAI_API_KEY")
    if config_modele["fournisseur"] != "anthropic" and cle_env and not os.environ.get(cle_env):
        print(f"{KO} {nom} : variable {cle_env} absente")
        return False

    base_url = config_modele.get("base_url") or ""
    if "11434" in base_url:
        if base_url not in cache_ollama:
            try:
                cache_ollama[base_url] = modeles_ollama(base_url)
            except Exception:
                print(f"{KO} {nom} : Ollama ne répond pas sur {base_url}. Ouvre l'application Ollama ou lance : ollama serve")
                return False
        if not modele_installe(config_modele["modele"], cache_ollama[base_url]):
            print(f"{KO} {nom} : modèle absent. Lance : ollama pull {config_modele['modele']}")
            return False

    debut = time.time()
    try:
        reponse = appeler_llm(config_modele, "Tu réponds en un seul mot.", "Réponds uniquement : OK", max_tokens=20)
    except Exception as erreur:
        print(f"{KO} {nom} : l'appel a échoué ({erreur})")
        return False
    duree = time.time() - debut
    print(f"{OK} {nom} répond en {duree:.1f} s : {reponse[:30]!r}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Vérifie que tout est prêt avant l'évaluation.")
    parser.add_argument("--config", default="config_local.yaml")
    args = parser.parse_args()

    print("1. Python et paquets")
    tout_va_bien = verifier_python() and verifier_paquets()
    if not tout_va_bien:
        return

    import yaml

    print(f"\n2. Configuration : {args.config}")
    chemin = RACINE / args.config
    if not chemin.exists():
        print(f"{KO} fichier introuvable : {chemin}")
        return
    config = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    actifs = [m for m in config["modeles_evalues"] if m.get("actif", True)]
    print(f"{OK} {len(actifs)} modèle(s) actif(s) : {', '.join(m['nom'] for m in actifs)}")

    print("\n3. Modèles à évaluer")
    cache = {}
    resultats = [verifier_modele(m, cache) for m in actifs]

    print("\n4. Juge")
    resultat_juge = verifier_modele(config["juge"], cache)

    print("\n5. Rappel")
    print("Vérifie que la longueur de contexte d'Ollama est au moins 8192 (Paramètres de l'application Ollama, ou variable OLLAMA_CONTEXT_LENGTH).")

    print()
    if all(resultats) and resultat_juge:
        print("Tout est prêt. Lance : python src/evaluer.py --config " + args.config)
    else:
        print("Corrige les lignes [PROBLÈME] puis relance cette vérification.")


if __name__ == "__main__":
    main()
