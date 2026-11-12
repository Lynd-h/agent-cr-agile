from pathlib import Path


def retirer_entete(texte):
    if texte.startswith("---"):
        fin = texte.find("\n---", 3)
        if fin != -1:
            return texte[fin + 4:].lstrip()
    return texte


def charger_prompt_skill(dossier_skill):
    dossier_skill = Path(dossier_skill)
    instructions = retirer_entete((dossier_skill / "SKILL.md").read_text(encoding="utf-8"))
    morceaux = [instructions]
    dossier_references = dossier_skill / "references"
    if dossier_references.exists():
        for fichier in sorted(dossier_references.glob("*.md")):
            contenu = fichier.read_text(encoding="utf-8")
            morceaux.append(f"\n\n---\n\nContenu du fichier references/{fichier.name} :\n\n{contenu}")
    return "".join(morceaux)


def construire_demande(transcription):
    return (
        "Voici la transcription de la réunion. Rédige le compte-rendu en suivant strictement tes instructions.\n\n"
        f"<transcription>\n{transcription}\n</transcription>"
    )
