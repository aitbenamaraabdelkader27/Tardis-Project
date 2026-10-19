from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/sncf_2018_2025.csv.gz"
MODEL_PATH = ROOT / "models/forecast.joblib"
REPORT_PATH = ROOT / "reports/metrics.json"
TARGET_COL = "Retard moyen de tous les trains à l'arrivée"
ROUTE_COLS = ["Service", "Gare de départ", "Gare d'arrivée"]
FEATURE_COLS = ["Date", *ROUTE_COLS]
TEXT_COMMENT_COLS = ["Commentaire annulations", "Commentaire retards au départ", "Commentaire retards à l'arrivée"]
