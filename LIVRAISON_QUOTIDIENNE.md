# Livraison quotidienne — une fiche par jour par e-mail

Destinataire : violette.drulang@gmail.com
Canaux : e-mail (lien de téléchargement direct du PDF) + dépôt GitHub (`sorties/`) + branche `main`.

## Protocole à chaque livraison

1. Rédiger la fiche du jour dans `contenus/` (format cours complet ou fiche thématique 14 sections selon le plan).
2. Générer le PDF : `python3 generer_fiche.py contenus/<fiche>.md`.
3. Commit + push sur `main` et `vibe/fiches-hebdo-678185`.
4. Envoyer l'e-mail à violette.drulang@gmail.com avec le lien raw.githubusercontent.com du PDF et un résumé de 3 lignes.

## File d'attente (ordre de priorité du plan stratégique)

| Jour | Fiche | Axe / thème IRA 2027 | Format |
|---|---|---|---|
| J1 | Fiche 2 — Fondements constitutionnels de l'administration (art. 20 à 74 C58) | Axe 1.B | Cours complet |
| J2 | Fiche 3 — Administration centrale et déconcentrée ; le préfet | Axe 2.A-C / thème 6 | Cours |
| J3 | Fiche 4 — Décentralisation : lois Defferre à la loi 3DS | Axe 3 / thème 6 | Cours |
| J4 | Fiche 5 — Finances publiques : LOLF, budget, dette | Axe 5 / thème 2 | Cours |
| J5 | Fiche 6 — Fonction publique et statut général | Axe 4 / thème 3 | Cours |
| J6 | Fiche 7 — Politiques publiques : conception, mise en œuvre, évaluation | Axe 6 / thème 3 | Cours |
| J7 | Fiche 8 — Système éducatif | Axe 7.A / thème 4 | Cours |
| J8 | Fiche 9 — Europe et administration multiniveaux | Axe 8 / thème 5 | Cours |
| J9 | Fiche 10 — Transformation numérique et IA dans l'administration | Axe 9 / thème 3 | Cours |
| J10 | Fiche 11 — Service public, usagers, cohésion territoriale | Axe 10 / thème 1 | Cours |
| J11 | Fiche 12 — Réforme de l'État et New Public Management | Axe 12 / thème 3 | Cours |
| J12+ | Fiches transversales par thème IRA 2027 + fiches de données chiffrées actualisées + fiches controverses | PLAN_STRATEGIQUE_IRA_2027.md | Fiches 14 sections |

## Règles

- Une seule fiche par jour, livrée le jour même de sa production.
- Chaque fiche respecte PRINCIPES.md, METHODE.md et le format cours (prose développée, références exactes, aucune source inventée).
- Toute donnée chiffrée est datée et sourcée ; en cas de doute, signalée comme à vérifier.
