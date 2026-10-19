import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from app.components.helpers import filter_data
from src.config import DATA_PATH, TARGET_COL, ROUTE_COLS
from src.data import eligible_rows, load_dataset, quality_report


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_dataset()

    def test_official_snapshot_integrity(self):
        source = json.loads(DATA_PATH.with_name("source.json").read_text())
        self.assertEqual(hashlib.sha256(gzip.decompress(DATA_PATH.read_bytes())).hexdigest(), source["sha256_uncompressed"])
        self.assertEqual(len(self.df), 11818)
        self.assertEqual(str(self.df.Date.min().date()), "2018-01-01")
        self.assertEqual(str(self.df.Date.max().date()), "2025-12-01")
        self.assertFalse(self.df.duplicated(["Date", *ROUTE_COLS]).any())
        pd.testing.assert_series_equal(self.df.Year, self.df.Date.dt.year, check_names=False)

    def test_quality_does_not_rewrite_observations(self):
        report = quality_report(self.df)
        self.assertEqual(report["eligible_rows"], 11745)
        self.assertEqual(report["excluded_rows"], 73)
        self.assertEqual(report["target_below_minus_30_min"], 9)
        self.assertLess(self.df[TARGET_COL].min(), -470)
        self.assertEqual(self.df[["Date", *ROUTE_COLS, TARGET_COL]].isna().sum().sum(), 0)

    def test_no_operated_trains_are_ineligible(self):
        eligible = self.df.loc[eligible_rows(self.df)]
        self.assertTrue((eligible["Nombre de circulations prévues"] > eligible["Nombre de trains annulés"]).all())

    def test_filters_and_empty_results(self):
        subset = filter_data(self.df, [2025], ["National"], "BORDEAUX ST JEAN", "PARIS MONTPARNASSE")
        self.assertGreater(len(subset), 0)
        self.assertTrue(subset.Year.eq(2025).all())
        self.assertTrue(subset[ROUTE_COLS[1]].eq("BORDEAUX ST JEAN").all())
        self.assertTrue(filter_data(self.df, [], []).empty)

    def test_corrupt_snapshot_fails_clearly(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv.gz"
            path.write_bytes(gzip.compress(b"incorrect"))
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_dataset(path)
