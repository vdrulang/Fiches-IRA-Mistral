# Fiches hebdomadaires automatisées — préparation IRA

Système de génération de fiches hebdomadaires en PDF à partir de fichiers Markdown,
conçu comme un outil de veille intellectuelle sur l'État et l'administration française.

Voir `MODULE_A.md` (mission et posture du module), `PROGRAMME.md` (les 12 axes de
recherche), `OBJECTIFS.md` (feuille de route, 13 capacités visées), `METHODE.md`
(hiérarchie des sources, protocole de recherche, règles de fiabilité),
`COMPETENCES.md` (compétences du concours IRA), `PLAN_ATTAQUE_2027.md` (plan d’attaque thèmes IRA 2027) et `PLAN_STRATEGIQUE_IRA_2027.md` (document stratégique complet), `VEILLE.md`, `LIVRAISON_QUOTIDIENNE.md` (une fiche par jour par e-mail) (veille permanente :
fréquences, rubriques, règles de sélection, format des actualités) et `PRINCIPES.md`
(règles de production transversales). Le format obligatoire des
fiches thématiques (14 sections) est défini dans `modeles/modele_fiche_thematique.md`.

## Arborescence

```
fiches-hebdo/
├── generer_fiche.py                  # convertisseur Markdown -> PDF
├── nouvelle_fiche.py                 # crée une nouvelle fiche de la semaine
├── construire_tout.py                # régénère tous les PDF
├── modeles/modele_fiche.md           # modèle de fiche hebdomadaire
├── modeles/modele_fiche_thematique.md # modèle de fiche thématique (14 sections)
├── contenus/                         # une fiche = un fichier .md
└── sorties/                          # les PDF générés
```

## Utilisation

Créer la fiche de la semaine (numéro ISO et dates lundi-dimanche calculés automatiquement) :

```bash
python3 nouvelle_fiche.py nom-du-theme
```

Rédiger le fichier créé dans `contenus/` (hebdomadaire : `modeles/modele_fiche.md`,
thématique : copier `modeles/modele_fiche_thematique.md`), puis générer le PDF :

```bash
python3 generer_fiche.py contenus/2025-S45_nom-du-theme.md
# ou tout regénérer :
python3 construire_tout.py
```

Automatisation hebdo (exemple cron, à exécuter le lundi matin) :

```cron
0 8 * * 1 cd /workspace/fiches-hebdo && python3 nouvelle_fiche.py veille && python3 construire_tout.py
```

## Format du fichier Markdown

Métadonnées en tête entre `---` :

```
---
titre: "Titre de la fiche"
semaine: "2025-S45"
periode: "du 03/11/2025 au 09/11/2025"
auteur: "..."
---
```

Corps : titres `#`, `##`, `###`, listes à puces ou numérotées, tableaux, `**gras**`, `*italique*`, citations avec `>`.

## Schémas dans les PDF (blocs ```schema)

Trois formes, détectées automatiquement :
- **Flux vertical** : `A --> B --> C` (flèches vers le bas, ex. hiérarchie des normes)
- **Organigramme** : racine en première ligne, enfants indentés de 2 espaces
- **Colonnes** : `A | B | C` (boîtes côte à côte avec flèches horizontales)

## Règles méthodologiques intégrées au modèle

- distinguer faits, analyses et opinions ;
- grille de lecture juridique, historique, politique, économique et budgétaire ;
- section dédiée aux incertitudes et vérifications à faire ;
- **aucune référence, statistique, jurisprudence ou citation ne doit être inventée** : seules les sources réellement consultées sont citées.

## Dépendances

`fpdf2`, `markdown-it-py`, `matplotlib` (fournit les polices DejaVu utilisées pour le PDF).

```bash
pip install fpdf2 markdown-it-py matplotlib
```
