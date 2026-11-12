from pathlib import Path

from verification import extraire_citations, verifier_citations, verifier_format

RACINE = Path(__file__).resolve().parent.parent

TRANSCRIPTION = "[10:06] Julie : Bon. Finalement on retire la 431 du sprint, on garde seulement la 430."

COMPTE_RENDU_COMPLET = """# Compte-rendu – Sprint Planning
## 1. Résumé
Texte.
## 2. Décisions
| 1 | On garde la 430 | « on garde seulement la 430 » |
## 3. Actions
Aucun élément dans la transcription.
## 4. Blocages et risques
Aucun élément dans la transcription.
## 5. Points ouverts
Aucun élément dans la transcription.
## 6. Informations manquantes ou ambiguës
- Responsable : Non précisé
"""


def test_citation_exacte_trouvee():
    resultat = verifier_citations("« Finalement on retire la 431 du sprint »", TRANSCRIPTION)
    assert resultat["taux_citations_exactes"] == 1.0


def test_citation_inventee_detectee():
    resultat = verifier_citations("« la mise en production est validée »", TRANSCRIPTION)
    assert resultat["taux_citations_exactes"] == 0.0
    assert resultat["citations_introuvables"] == ["la mise en production est validée"]


def test_majuscules_et_ponctuation_ignorees():
    resultat = verifier_citations("« FINALEMENT, on retire la 431 du sprint ! »", TRANSCRIPTION)
    assert resultat["taux_citations_exactes"] == 1.0


def test_citation_coupee_avec_points_de_suspension():
    resultat = verifier_citations("« Finalement on retire… seulement la 430 »", TRANSCRIPTION)
    assert resultat["taux_citations_exactes"] == 1.0


def test_aucune_citation():
    resultat = verifier_citations("Pas de preuve ici.", TRANSCRIPTION)
    assert resultat["nb_citations"] == 0
    assert resultat["taux_citations_exactes"] is None


def test_non_precise_n_est_pas_une_citation():
    assert extraire_citations("« Non précisé »") == []


def test_format_complet():
    resultat = verifier_format(COMPTE_RENDU_COMPLET)
    assert resultat["sections_presentes"] == 6
    assert resultat["ordre_respecte"] is True


def test_format_incomplet():
    resultat = verifier_format("## 1. Résumé\nTexte\n## 3. Actions\nTexte")
    assert resultat["sections_presentes"] == 2


def test_ordre_non_respecte():
    resultat = verifier_format("## 2. Décisions\n## 1. Résumé")
    assert resultat["ordre_respecte"] is False


def test_les_exemples_du_skill_sont_corrects():
    contenu = (RACINE / "skill" / "compte-rendu-agile" / "references" / "exemples.md").read_text(encoding="utf-8")
    for exemple in contenu.split("## Exemple")[1:]:
        transcription = exemple.split("### Transcription")[1].split("### Compte-rendu attendu")[0]
        compte_rendu = exemple.split("### Compte-rendu attendu")[1]
        assert verifier_citations(compte_rendu, transcription)["taux_citations_exactes"] == 1.0
        assert verifier_format(compte_rendu)["sections_presentes"] == 6
