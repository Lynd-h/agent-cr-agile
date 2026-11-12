import re

MOTIFS = [
    ("IBAN", r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}(?:\s?[A-Z0-9]{1,3})?\b"),
    ("CARTE", r"\b(?:\d{4}[\s-]?){3}\d{4}\b"),
    ("EMAIL", r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"),
    ("TELEPHONE", r"(?:\+33\s?|\b0)[1-9](?:[\s.-]?\d{2}){4}\b"),
]


class Masqueur:
    def __init__(self, personnes=None, clients=None):
        self.listes = [("PERSONNE", personnes or []), ("CLIENT", clients or [])]
        self.correspondances = {}
        self.compteurs = {}

    def _etiquette(self, categorie, valeur):
        cle = (categorie, valeur.lower())
        if cle not in self.correspondances:
            self.compteurs[categorie] = self.compteurs.get(categorie, 0) + 1
            etiquette = f"[{categorie}_{self.compteurs[categorie]}]"
            self.correspondances[cle] = (etiquette, valeur)
        return self.correspondances[cle][0]

    def masquer(self, texte):
        for categorie, motif in MOTIFS:
            texte = re.sub(motif, lambda m, c=categorie: self._etiquette(c, m.group(0)), texte)
        for categorie, valeurs in self.listes:
            for valeur in sorted(valeurs, key=len, reverse=True):
                motif = r"(?<!\w)" + re.escape(valeur) + r"(?!\w)"
                texte = re.sub(
                    motif,
                    lambda m, c=categorie: self._etiquette(c, m.group(0)),
                    texte,
                    flags=re.IGNORECASE,
                )
        return texte

    def demasquer(self, texte):
        for etiquette, valeur in self.correspondances.values():
            texte = texte.replace(etiquette, valeur)
        return texte

    def resume(self):
        return dict(self.compteurs)
