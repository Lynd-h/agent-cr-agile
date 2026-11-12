import re
import unicodedata

SECTIONS = [
    "1. Résumé",
    "2. Décisions",
    "3. Actions",
    "4. Blocages et risques",
    "5. Points ouverts",
    "6. Informations manquantes ou ambiguës",
]


def normaliser(texte):
    texte = unicodedata.normalize("NFKC", texte).lower()
    texte = texte.replace("’", "'")
    texte = re.sub(r"[^\w\s']", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()


def extraire_citations(compte_rendu):
    citations = re.findall(r"«\s*(.+?)\s*»", compte_rendu)
    return [c for c in citations if normaliser(c) not in ("", "non précisé")]


def citation_presente(citation, transcription_normalisee):
    morceaux = [normaliser(m) for m in re.split(r"\.\.\.|…", citation)]
    morceaux = [m for m in morceaux if m]
    return bool(morceaux) and all(m in transcription_normalisee for m in morceaux)


def verifier_citations(compte_rendu, transcription):
    transcription_normalisee = normaliser(transcription)
    citations = extraire_citations(compte_rendu)
    introuvables = [c for c in citations if not citation_presente(c, transcription_normalisee)]
    taux = None
    if citations:
        taux = round((len(citations) - len(introuvables)) / len(citations), 3)
    return {
        "nb_citations": len(citations),
        "taux_citations_exactes": taux,
        "citations_introuvables": introuvables,
    }


def verifier_format(compte_rendu):
    titres = [normaliser(t) for t in re.findall(r"^##\s+(.+)$", compte_rendu, flags=re.MULTILINE)]
    presentes = [s for s in SECTIONS if normaliser(s) in titres]
    ordre_respecte = [t for t in titres if t in [normaliser(s) for s in SECTIONS]] == [
        normaliser(s) for s in SECTIONS if normaliser(s) in titres
    ]
    return {
        "sections_presentes": len(presentes),
        "taux_format": round(len(presentes) / len(SECTIONS), 3),
        "ordre_respecte": ordre_respecte,
    }


def detecter_fuites(compte_rendu, masqueur):
    fuites = []
    for _, valeur in masqueur.correspondances.values():
        if normaliser(valeur) and normaliser(valeur) in normaliser(compte_rendu):
            fuites.append(valeur)
    return fuites
