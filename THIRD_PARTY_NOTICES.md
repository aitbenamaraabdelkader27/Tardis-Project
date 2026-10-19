# Attribution and publication rights

## SNCF data

Contains information from **SNCF Voyageurs**, “Régularité mensuelle TGV par liaisons (AQST)”,
retrieved 16 October 2026 from:
https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/

The publisher identifies its license as **Open Database License (ODbL)**:
https://opendatacommons.org/licenses/odbl/1-0/
Publisher terms: https://data.sncf.com/pages/cgu/A1#A1

The included compressed snapshot restricts the source to 2018–2025 and orders rows.
The loader renames fields using the publisher schema, parses dates/numbers and
normalises surrounding whitespace. The application excludes rows without operated
trains from analysis/modelling. It does not invent, clip or impute observed targets.
Source data, metadata and checksum are included; export CSVs are derived from this
ODbL-licensed data and retain this attribution. Redistributors should retain this
notice and the applicable database license, including its share-alike requirements.

## Collective project

The initial TARDIS code, notebooks and reports were developed as a collective
EPITECH project. No claim of sole authorship is made. No new software license is
asserted for the team's code. The repository owner must confirm redistribution
rights and team attribution before public release. Assignment statements and
restricted grading materials must not be included. The public-export script
excludes historical coursework assets and git history but does not determine rights.
