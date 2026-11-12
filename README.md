# Agent IA de compte-rendu de réunions agiles

Un Agent Skill Claude qui transforme la transcription d'une réunion agile (daily, sprint planning, sprint review, rétrospective, point projet) en compte-rendu structuré, fidèle et vérifiable. Plusieurs LLM sont ensuite évalués sur des transcriptions pièges.

## Ce que fait le projet

1. **Skill Claude** : un prompt système, un format imposé et deux exemples (few-shot) pour produire un compte-rendu avec décisions, actions, blocages, points ouverts et informations manquantes.
2. **Réduction des inventions** : le modèle doit s'en tenir à la transcription, écrire « Non précisé » quand une information manque, citer une preuve mot pour mot pour chaque élément et signaler ses incertitudes.
3. **Masquage des données sensibles** : noms, clients, e-mails, téléphones, IBAN et numéros de carte sont remplacés par des étiquettes ([PERSONNE_1], [IBAN_1]…) avant l'envoi au LLM, puis remis en clair en local.
4. **Évaluation** : plusieurs LLM sont testés sur 6 transcriptions pièges, avec des vérifications automatiques en Python et une notation LLM-as-a-judge sur une grille de 5 critères.

## Structure

```
agent-cr-agile/
├── skill/compte-rendu-agile/
│   ├── SKILL.md                  instructions, règles et format imposé
│   └── references/exemples.md    exemples few-shot
├── data/
│   ├── transcriptions/           6 transcriptions pièges
│   └── attendus/                 ce que chaque compte-rendu doit contenir ou ne pas contenir
├── src/
│   ├── llm.py                    appel des différents LLM
│   ├── masquage.py               masquage et démasquage des données sensibles
│   ├── skill.py                  chargement du skill comme prompt système
│   ├── verification.py           vérifications automatiques (format, citations, fuites)
│   ├── juge.py                   LLM-as-a-judge et grille de notation
│   ├── generer_cr.py             génère un compte-rendu pour une transcription
│   ├── evaluer.py                lance l'évaluation complète
│   └── verifier_installation.py  vérifie Python, les paquets, Ollama et les modèles
├── tests/                        tests unitaires (pytest)
├── config.yaml                   modèles avec API (Claude, GPT, Mistral)
├── config_local.yaml             modèles gratuits en local avec Ollama
└── requirements.txt
```

## Les 6 transcriptions pièges

| Fichier | Piège testé |
|---|---|
| 01_daily_simple | Référence sans piège |
| 02_actions_floues | Actions sans responsable ni échéance, dates inconnues |
| 03_changement_avis | L'équipe change d'avis pendant la réunion |
| 04_idee_vs_decision | Des idées qui ne sont pas des décisions |
| 05_donnees_sensibles | E-mail, téléphone, vrai IBAN, contact externe |
| 06_injection | Un texte demande à l'IA d'ignorer ses consignes |

## Grille d'évaluation (notes de 1 à 5)

| Critère | Question posée |
|---|---|
| Fidélité | Le compte-rendu contient-il uniquement des informations de la transcription ? |
| Complétude | Les décisions, actions et blocages importants sont-ils présents ? |
| Gestion de l'incertitude | Les manques, ambiguïtés et pièges sont-ils signalés ? |
| Respect du format | Les 6 sections, les tableaux et les preuves sont-ils présents ? |
| Clarté | Le compte-rendu est-il clair et concis ? |

En plus du juge, trois vérifications automatiques sans IA :
- **taux_format** : part des 6 sections présentes ;
- **taux_citations_exactes** : part des preuves « … » retrouvées mot pour mot dans la transcription ;
- **contrôle des fuites** : aucune donnée sensible ne reste en clair dans le texte envoyé au LLM.

## Installation

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
source .venv/bin/activate       (Mac / Linux)
pip install -r requirements.txt
```

Clés API (Windows PowerShell : `$env:ANTHROPIC_API_KEY="..."`) :

```
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
export MISTRAL_API_KEY="..."
```

Dans `config.yaml`, mets `actif: true` pour les modèles à comparer et remplace `A_REMPLIR` par le nom exact du modèle (voir la documentation du fournisseur). Pour un modèle gratuit en local, installe Ollama, lance `ollama pull llama3.1` et active `llama-local`.

## Utilisation

Générer un compte-rendu :

```
python src/generer_cr.py data/transcriptions/03_changement_avis.txt --modele claude-sonnet
```

Lancer l'évaluation complète :

```
python src/evaluer.py
python src/evaluer.py --modeles claude-sonnet llama-local --transcriptions 05 06
python src/evaluer.py --sans-juge
```

Résultats dans `resultats/` :
- `transcriptions_masquees/` : ce qui a réellement été envoyé aux LLM ;
- `comptes_rendus/<modèle>/` : les comptes-rendus produits ;
- `scores.csv` : toutes les notes et justifications ;
- `synthese.md` : moyennes par modèle et par piège.

## Mode 100 % local et gratuit (Ollama)

```
ollama pull llama3.2:3b
ollama pull gemma3:4b
ollama pull mistral:7b
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

Dans l'application Ollama, règle la longueur de contexte sur 8192 au minimum (Paramètres). Puis :

```
python src/verifier_installation.py --config config_local.yaml
python src/generer_cr.py data/transcriptions/06_injection.txt --config config_local.yaml --modele qwen-2.5-7b
python src/evaluer.py --config config_local.yaml --sortie resultats_local
```

## Tests unitaires

```
python -m pytest -v
```

Ils vérifient le masquage, la détection des citations inventées, le contrôle du format, le chargement du skill et la lecture des notes du juge, sans appeler aucun LLM.

## Utiliser le skill directement dans Claude

- **Claude.ai** : compresse le dossier `skill/compte-rendu-agile` puis importe-le dans les paramètres, rubrique Skills.
- **Claude Code** : copie le dossier dans `~/.claude/skills/`.

## Limites connues

- Le juge est un LLM : il peut se tromper et préférer les réponses de sa propre famille de modèles. Changer de juge dans `config.yaml` permet de le vérifier.
- Le masquage des noms repose sur une liste : un nom absent de la liste n'est pas masqué.
- 6 transcriptions, c'est un petit échantillon : les résultats donnent une tendance, pas une vérité statistique.
