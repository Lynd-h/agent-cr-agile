# Exemples de comptes-rendus

## Exemple 1 : daily avec un blocage et une idée non tranchée

### Transcription

```
Réunion : Daily – équipe Portail
[09:15] Léa (Scrum Master) : On commence. Hugo ?
[09:15] Hugo (développeur) : J'ai terminé la page de connexion. Aujourd'hui je commence la page profil.
[09:16] Inès (testeuse) : Je suis bloquée, l'environnement de test ne répond plus depuis ce matin.
[09:16] Léa (Scrum Master) : Je préviens l'équipe infra tout de suite.
[09:17] Hugo (développeur) : Il faudrait aussi qu'on mette à jour la librairie de graphiques un jour.
[09:17] Léa (Scrum Master) : Ok, on garde ça en tête. Merci à tous.
```

### Compte-rendu attendu

```
# Compte-rendu – Daily

**Date :** Non précisé
**Participants :** Léa (Scrum Master), Hugo (développeur), Inès (testeuse)

## 1. Résumé
Hugo a terminé la page de connexion et commence la page profil. Inès est bloquée car l'environnement de test ne répond plus. Léa prévient l'équipe infra.

## 2. Décisions
Aucun élément dans la transcription.

## 3. Actions
| # | Action | Responsable | Échéance | Preuve |
|---|---|---|---|---|
| 1 | Commencer la page profil | Hugo | Aujourd'hui | « Aujourd'hui je commence la page profil » |
| 2 | Prévenir l'équipe infra de la panne de l'environnement de test | Léa | Tout de suite | « Je préviens l'équipe infra tout de suite » |

## 4. Blocages et risques
| # | Blocage ou risque | Signalé par | Preuve |
|---|---|---|---|
| 1 | L'environnement de test ne répond plus depuis ce matin | Inès | « l'environnement de test ne répond plus depuis ce matin » |

## 5. Points ouverts
- Mise à jour de la librairie de graphiques : proposée par Hugo, sans décision.

## 6. Informations manquantes ou ambiguës
- La date de la réunion n'est pas indiquée.
- La mise à jour de la librairie de graphiques n'a ni responsable ni échéance (« un jour »).
```

## Exemple 2 : changement d'avis et données masquées

### Transcription

```
Réunion : Sprint Planning – Sprint 8
Date : 12 mars 2026
[10:00] [PERSONNE_1] (Product Owner) : Je propose de livrer la nouvelle recherche vendredi.
[10:01] [PERSONNE_2] (développeur) : Vendredi c'est trop juste, les tests ne seront pas finis.
[10:02] [PERSONNE_1] (Product Owner) : D'accord, on décale : la livraison se fera mardi prochain.
[10:02] [PERSONNE_3] (testeur) : Je finis les tests lundi.
[10:03] [PERSONNE_1] (Product Owner) : Et j'envoie le planning à [EMAIL_1] après la réunion.
```

### Compte-rendu attendu

```
# Compte-rendu – Sprint Planning

**Date :** 12 mars 2026
**Participants :** [PERSONNE_1] (Product Owner), [PERSONNE_2] (développeur), [PERSONNE_3] (testeur)

## 1. Résumé
La livraison de la nouvelle recherche est décalée à mardi prochain car les tests ne seraient pas finis vendredi. [PERSONNE_3] finit les tests lundi et [PERSONNE_1] envoie le planning après la réunion.

## 2. Décisions
| # | Décision | Preuve |
|---|---|---|
| 1 | La livraison de la nouvelle recherche se fera mardi prochain | « on décale : la livraison se fera mardi prochain » |

## 3. Actions
| # | Action | Responsable | Échéance | Preuve |
|---|---|---|---|---|
| 1 | Finir les tests | [PERSONNE_3] | Lundi | « Je finis les tests lundi » |
| 2 | Envoyer le planning à [EMAIL_1] | [PERSONNE_1] | Après la réunion | « j'envoie le planning à [EMAIL_1] après la réunion » |

## 4. Blocages et risques
| # | Blocage ou risque | Signalé par | Preuve |
|---|---|---|---|
| 1 | Les tests ne seraient pas finis pour une livraison vendredi | [PERSONNE_2] | « Vendredi c'est trop juste, les tests ne seront pas finis » |

## 5. Points ouverts
Aucun élément dans la transcription.

## 6. Informations manquantes ou ambiguës
- Changement d'avis : la livraison était d'abord proposée vendredi, puis décalée à mardi prochain. Seule la décision finale est retenue.
- « Mardi prochain » est une date relative : la date exacte n'est pas précisée.
```
