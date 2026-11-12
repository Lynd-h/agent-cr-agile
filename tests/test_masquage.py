from pathlib import Path

from masquage import Masqueur
from verification import detecter_fuites

RACINE = Path(__file__).resolve().parent.parent


def nouveau_masqueur():
    return Masqueur(["Pierre Lambert", "Sarah", "Karim", "Julie", "Thomas", "Nadia", "Marc"], ["Altaris"])


def test_email_masque():
    masqueur = nouveau_masqueur()
    texte = masqueur.masquer("Écris à jean.dupont@exemple.fr demain.")
    assert "jean.dupont@exemple.fr" not in texte
    assert "[EMAIL_1]" in texte


def test_telephone_masque():
    masqueur = nouveau_masqueur()
    for numero in ["06 12 34 56 78", "0612345678", "+33 6 12 34 56 78", "06.12.34.56.78"]:
        assert numero not in masqueur.masquer(f"Appelle le {numero}.")


def test_iban_masque():
    masqueur = nouveau_masqueur()
    texte = masqueur.masquer("IBAN : FR76 3000 6000 0112 3456 7890 189.")
    assert "3000" not in texte
    assert "[IBAN_1]" in texte


def test_carte_masquee():
    masqueur = nouveau_masqueur()
    texte = masqueur.masquer("Carte 4970 1012 3456 7890 expirée.")
    assert "4970" not in texte


def test_noms_et_clients_masques():
    masqueur = nouveau_masqueur()
    texte = masqueur.masquer("Pierre Lambert travaille chez Altaris avec Sarah.")
    assert "Pierre" not in texte and "Altaris" not in texte and "Sarah" not in texte
    assert "[PERSONNE_1]" in texte and "[CLIENT_1]" in texte


def test_meme_valeur_meme_etiquette():
    masqueur = nouveau_masqueur()
    texte = masqueur.masquer("Sarah parle. Ensuite sarah répond.")
    assert texte.count("[PERSONNE_1]") == 2


def test_nom_dans_un_autre_mot_non_masque():
    masqueur = Masqueur(["Marc"], [])
    assert masqueur.masquer("Marcel est là.") == "Marcel est là."


def test_demasquage_redonne_le_texte_original():
    masqueur = nouveau_masqueur()
    original = (RACINE / "data" / "transcriptions" / "05_donnees_sensibles.txt").read_text(encoding="utf-8")
    assert masqueur.demasquer(masqueur.masquer(original)) == original


def test_aucune_fuite_dans_les_transcriptions():
    for fichier in (RACINE / "data" / "transcriptions").glob("*.txt"):
        masqueur = nouveau_masqueur()
        texte_masque = masqueur.masquer(fichier.read_text(encoding="utf-8"))
        assert detecter_fuites(texte_masque, masqueur) == [], fichier.name
