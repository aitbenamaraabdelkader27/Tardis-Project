# Official SNCF snapshot

Publisher: **SNCF Voyageurs**. Dataset: [Régularité mensuelle TGV par liaisons (AQST)](https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/).
License: **Open Database License (ODbL)**; see [attribution](../THIRD_PARTY_NOTICES.md).

`sncf_2018_2025.csv.gz` is the official CSV compressed without changing its values,
restricted to January 2018–December 2025, sorted by date/service/origin/destination.
Retrieved 16 October 2026. 11,818 rows, 26 fields, 752,669 compressed bytes.
`source.json` records the URL, timestamp, original schema and uncompressed SHA-256.
The loader checks that hash before parsing. No API request is made at app startup.

## Data contract and units

One row = one directed route, service and calendar month. Date is published as
YYYY-MM and parsed as a first-of-month timestamp. Duration and delays are in minutes;
counts are train counts; cause shares are percentages. Service/stations/comments
are text. Numeric values are parsed from the official schema. Year and month are
computed from Date, never trusted from a legacy file.

Only route identity and the forecast calendar are prospective features. The selected
route-mean baseline uses route identity only. Duration is a **monthly observed average**,
not an individual scheduled duration. Even planned train counts in this snapshot may
be revised after the month: none are used as predictors. All operational outcomes,
comments and delay-cause percentages are excluded from features.

## Quality policy

No duplicate route-month keys; no missing date, route identity or target. Two comment
columns are entirely missing and arrival comments are missing in 11,120 rows; this is
not evidence that no disruption occurred. There are 119 signed negative targets,
nine below −30 minutes, including an extreme −472.639-minute source value, and
43 negative cells in `nb_train_retard_sup_30`. These remain unresolved source anomalies.
We do not replace them by zero, fabricate a plausible value or silently trim outliers.
The negative auxiliary count is not used in prediction or dashboard KPIs.

Eligibility requires date, complete route identity, finite target, nonnegative
cancellations and scheduled trains greater than cancellations. This excludes
73 no-operated-train months and leaves 11,745 observations for analysis/modelling.
Targets are not imputed. Both candidates and baselines use exactly this cohort.
Full per-column missingness and dtypes are in `reports/metrics.json` and available via
`python -m src.data_checks`.

An observed signed average can reflect early arrival; very negative values are not
verified as genuine early arrivals. Retaining these values makes the limitation
visible and can materially affect training and scores. A domain-reviewed quality
policy should precede any operational forecast.

The source warns that a train can appear in several route observations. Dashboard
means are unweighted means of route-month values, not global SNCF regularity.
The snapshot is TGV routes reported to AQST, not all SNCF trains or stations.

## Reproduction and refresh

Use the committed snapshot to reproduce published scores. To explicitly download a
new 2018–2025 export, run `python scripts/fetch_data.py`, then retrain and test.
The official API is mutable and can revise historical records; the new download may
have a different hash, even with the same query. Review and version the resulting
snapshot, manifest, artifacts and metrics together. No random sampling is performed.

`project_dataset.csv` and the root `cleaned_dataset.csv` are historical educational
assets archived outside the personal repository (see `docs/CLEANUP.md`). Their precise alteration history
is unknown; they are not loaded by the app and are excluded from the public export.

## Dictionary of source fields

French labels are retained internally to preserve continuity with the original
project. Public tables and axes use English labels. `source.json` preserves the exact
SNCF field identifiers; types below describe the official schema.

| Source field | Publisher label | Type | Use |
|---|---|---|---|
| `date` | Date | date | Forecast month |
| `service` | Service | text | Route identity |
| `gare_depart` | Gare de départ | text | Route identity |
| `gare_arrivee` | Gare d'arrivée | text | Route identity |
| `duree_moyenne` | Durée moyenne du trajet | int | Descriptive only; excluded from predictors |
| `nb_train_prevu` | Nombre de circulations prévues | int | Descriptive only; excluded from predictors |
| `nb_annulation` | Nombre de trains annulés | int | Descriptive only; excluded from predictors |
| `commentaire_annulation` | Commentaire annulations | text | Descriptive only; excluded from predictors |
| `nb_train_depart_retard` | Nombre de trains en retard au départ | int | Descriptive only; excluded from predictors |
| `retard_moyen_depart` | Retard moyen des trains en retard au départ | double | Descriptive only; excluded from predictors |
| `retard_moyen_tous_trains_depart` | Retard moyen de tous les trains au départ | double | Descriptive only; excluded from predictors |
| `commentaire_retards_depart` | Commentaire retards au départ | text | Descriptive only; excluded from predictors |
| `nb_train_retard_arrivee` | Nombre de trains en retard à l'arrivée | int | Descriptive only; excluded from predictors |
| `retard_moyen_arrivee` | Retard moyen des trains en retard à l'arrivée | double | Descriptive only; excluded from predictors |
| `retard_moyen_tous_trains_arrivee` | Retard moyen de tous les trains à l'arrivée | double | Observed target (minutes) |
| `commentaires_retard_arrivee` | Commentaire retards à l'arrivée | text | Descriptive only; excluded from predictors |
| `nb_train_retard_sup_15` | Nombre trains en retard > 15min | int | Descriptive only; excluded from predictors |
| `retard_moyen_trains_retard_sup15` | Retard moyen trains en retard > 15 (si liaison concurrencée par vol) | double | Descriptive only; excluded from predictors |
| `nb_train_retard_sup_30` | Nombre trains en retard > 30min | int | Descriptive only; excluded from predictors |
| `nb_train_retard_sup_60` | Nombre trains en retard > 60min | int | Descriptive only; excluded from predictors |
| `prct_cause_externe` | Prct retard pour causes externes | double | Descriptive only; excluded from predictors |
| `prct_cause_infra` | Prct retard pour cause infrastructure | double | Descriptive only; excluded from predictors |
| `prct_cause_gestion_trafic` | Prct retard pour cause gestion trafic | double | Descriptive only; excluded from predictors |
| `prct_cause_materiel_roulant` | Prct retard pour cause matériel roulant | double | Descriptive only; excluded from predictors |
| `prct_cause_gestion_gare` | Prct retard pour cause gestion en gare et réutilisation de matériel | double | Descriptive only; excluded from predictors |
| `prct_cause_prise_en_charge_voyageurs` | Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances) | double | Descriptive only; excluded from predictors |
