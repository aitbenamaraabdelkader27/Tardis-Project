import unittest
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from src.config import ROOT


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "tardis_dashboard.py"), default_timeout=30).run()
        self.assertEqual(len(self.app.exception), 0)

    def navigate(self, page):
        self.app.sidebar.radio[0].set_value(page).run()
        self.assertEqual(len(self.app.exception), 0)

    def test_overview_and_performance_render(self):
        self.assertEqual(len(self.app.metric), 4)
        self.assertEqual(len(self.app.get("plotly_chart")), 2)
        self.navigate("Model Performance")
        self.assertEqual(len(self.app.metric), 3)
        self.assertEqual(len(self.app.get("plotly_chart")), 3)
        self.assertGreater(len(self.app.dataframe), 0)

    def test_explorer_filters_and_empty_state(self):
        self.navigate("Data Explorer")
        self.assertEqual(len(self.app.get("plotly_chart")), 3)
        self.app.multiselect[0].set_value([2025]).run()
        self.assertEqual(len(self.app.exception), 0)
        self.app.multiselect[0].set_value([]).run()
        self.assertEqual(len(self.app.exception), 0)
        self.assertEqual(len(self.app.get("plotly_chart")), 0)
        self.assertTrue(any("No observations" in element.value for element in self.app.info))

    def test_prediction_submit_and_dependent_stations(self):
        self.navigate("Delay Prediction")
        for service in ["National", "International"]:
            self.app.selectbox[0].set_value(service).run()
            self.assertGreater(len(self.app.selectbox[1].options), 0)
            self.assertGreater(len(self.app.selectbox[2].options), 0)
            self.app.button[0].click().run()
            self.assertEqual(len(self.app.exception), 0)
            self.assertEqual(len(self.app.metric), 1)
            self.assertTrue(self.app.metric[0].value.endswith(" min"))

    def test_missing_artifact_has_actionable_error(self):
        st.cache_resource.clear()
        try:
            with patch("src.inference.load_artifacts", side_effect=FileNotFoundError("test missing artifact")):
                self.navigate("Model Performance")
                self.assertEqual(len(self.app.error), 1)
                self.assertIn("matching model artifact", self.app.error[0].value)
        finally:
            st.cache_resource.clear()

    def test_missing_data_has_actionable_error(self):
        st.cache_data.clear()
        try:
            with patch("src.data.load_dataset", side_effect=FileNotFoundError("test missing dataset")):
                self.app.run()
                self.assertEqual(len(self.app.exception), 0)
                self.assertEqual(len(self.app.error), 1)
                self.assertIn("versioned dataset", self.app.error[0].value)
        finally:
            st.cache_data.clear()
