"""TARDIS: a frozen, verifiable monthly railway forecasting demonstration."""
from datetime import date
import json
import logging
import pandas as pd
import plotly.express as px
import streamlit as st
from app.components.charts import polish
from app.components.helpers import filter_data
from src.config import DATA_PATH, REPORT_PATH, ROUTE_COLS, TARGET_COL
from src.data import eligible_rows, load_dataset
from src.inference import load_artifacts, predict_month

st.set_page_config(page_title="TARDIS · Railway insights", page_icon="🚆", layout="wide")
st.markdown("""<style>
.block-container {max-width:1280px;padding-top:2.5rem;padding-bottom:3rem;}
h1 {font-weight:650;letter-spacing:-.045em;} h2,h3 {letter-spacing:-.025em;}
[data-testid="stMetric"] {background:#f2f6f4;border:1px solid #e1eae5;border-radius:12px;padding:20px;}
[data-testid="stMetricLabel"] {color:#536a62;}
[data-testid="stSidebar"] {background:#f2f6f4;}
</style>""", unsafe_allow_html=True)


@st.cache_data
def data_cache():
    return load_dataset()


@st.cache_resource
def artifact_cache():
    return load_artifacts()


st.sidebar.markdown("## TARDIS")
st.sidebar.caption("RAILWAY DATA · MACHINE LEARNING")
page = st.sidebar.radio("Explore TARDIS", ["Overview", "Data Explorer", "Delay Prediction", "Model Performance"])
st.sidebar.divider()
st.sidebar.caption("SNCF Voyageurs · Open Data · ODbL\n\nMonthly observations, 2018–2025")
st.sidebar.link_button("View official dataset", "https://ressources.data.sncf.com/explore/dataset/regularite-mensuelle-tgv-aqst/")
st.sidebar.caption("An EPITECH team project, revisited for a reproducible portfolio demonstration.")

try:
    raw = data_cache()
    df = raw.loc[eligible_rows(raw)].copy()
except Exception:
    logging.exception("Dataset loading failed")
    st.error("The versioned dataset could not be loaded. Restore data/sncf_2018_2025.csv.gz and data/source.json from the repository.")
    st.stop()

st.caption("TARDIS / " + page.upper())
st.title({"Overview": "Railway delays, in perspective.", "Data Explorer": "Explore the monthly record.",
          "Delay Prediction": "Estimate a route’s monthly delay.", "Model Performance": "Evidence behind the estimate."}[page])
st.markdown("Historical TGV route data, transparent modelling and a clear view of what the numbers can tell us.")

if page == "Overview":
    st.info("Each observation describes one route in one month. Predictions estimate its average arrival delay in minutes; they do not track an individual train.")
    kpis = st.columns(4)
    kpis[0].metric("Eligible route-months", f"{len(df):,}")
    kpis[1].metric("Directed routes", f"{len(df[ROUTE_COLS].drop_duplicates()):,}")
    kpis[2].metric("Mean arrival delay", f"{df[TARGET_COL].mean():.2f} min")
    kpis[3].metric("History", "2018–2025")
    st.caption("Delay KPI: unweighted mean across eligible route-months. It is not a network-wide SNCF punctuality measure.")
    trend = df.groupby(["Date", "Service"], as_index=False)[TARGET_COL].mean()
    st.plotly_chart(polish(px.line(trend, x="Date", y=TARGET_COL, color="Service", title="Monthly average arrival delay by service",
                                   labels={"Date": "Month", TARGET_COL: "Average arrival delay (min)"})), width="stretch")
    left, right = st.columns(2)
    with left:
        full_range = st.checkbox("Show full source range", key="overview_range")
        central = df[TARGET_COL].between(-5, 40)
        distribution = df if full_range else df.loc[central]
        st.plotly_chart(polish(px.histogram(distribution, x=TARGET_COL, nbins=40, title="Distribution of route-month averages",
                                           labels={TARGET_COL: "Arrival delay (min)"})), width="stretch")
        if not full_range:
            st.caption(f"Histogram view: −5 to 40 minutes; {(~central).sum()} observations outside this range. KPIs and model scores retain all eligible observations.")
    with right:
        st.subheader("Read the data with care")
        st.write("The official snapshot includes signed delays and source anomalies, including extreme negative values. These are retained rather than replaced with invented outcomes.")
        st.write(f"{len(raw) - len(df):,} observations are excluded by the eligibility rules, primarily months with no operated trains. Explore the quality report for details.")
        st.write("Routes can overlap: the same train may appear on multiple routes. Route counts and averages must not be interpreted as distinct trains or overall TGV regularity.")
    with st.expander("Provenance and data quality"):
        source = json.loads(DATA_PATH.with_name("source.json").read_text())
        st.write(f"Publisher: {source['publisher']} · Retrieved: {source['retrieved_at'][:10]} · License: {source['license']}")
        st.code(source["sha256_uncompressed"], language=None)
        st.write("Small negative averages can reflect early arrivals; very large negative values are unresolved source-quality issues. No targets are clipped or imputed.")

elif page == "Data Explorer":
    c1, c2 = st.columns(2)
    years = c1.multiselect("Years", sorted(df.Year.unique().tolist()), default=sorted(df.Year.unique().tolist()))
    services = c2.multiselect("Services", sorted(df.Service.unique()), default=sorted(df.Service.unique()))
    c3, c4 = st.columns(2)
    departure = c3.selectbox("Departure station", ["All stations", *sorted(df[ROUTE_COLS[1]].unique())])
    arrival = c4.selectbox("Arrival station", ["All stations", *sorted(df[ROUTE_COLS[2]].unique())])
    filtered = filter_data(df, years, services, departure, arrival)
    st.caption(f"{len(filtered):,} matching route-months · All chart averages weight each route-month equally.")
    if filtered.empty:
        st.info("No observations match these filters. Select another route, service or year.")
    else:
        monthly = filtered.groupby("Date", as_index=False)[TARGET_COL].mean()
        st.plotly_chart(polish(px.line(monthly, x="Date", y=TARGET_COL, markers=True, title="Arrival delay over time",
                                       labels={"Date": "Month", TARGET_COL: "Average arrival delay (min)"})), width="stretch")
        a, b = st.columns(2)
        with a:
            full_range = st.checkbox("Show full source range", key="explorer_range")
            central = filtered[TARGET_COL].between(-5, 40)
            distribution = filtered if full_range else filtered.loc[central]
            st.plotly_chart(polish(px.histogram(distribution, x=TARGET_COL, nbins=40, title="Delay distribution", labels={TARGET_COL: "Arrival delay (min)"})), width="stretch")
            if not full_range:
                st.caption(f"Histogram view: −5 to 40 minutes; {(~central).sum()} observations outside this range. Other charts, downloads and model scores retain all filtered observations.")
        with b:
            comparison = filtered.groupby(ROUTE_COLS[1], as_index=False).agg(delay=(TARGET_COL, "mean"), observations=(TARGET_COL, "size")).nlargest(12, "delay")
            st.plotly_chart(polish(px.bar(comparison, x="delay", y=ROUTE_COLS[1], orientation="h", hover_data=["observations"],
                                         title="Departure stations · highest mean delays", labels={"delay": "Arrival delay (min)", ROUTE_COLS[1]: "Station"})), width="stretch")
        view = filtered[["Date", *ROUTE_COLS, TARGET_COL, "Nombre de circulations prévues", "Nombre de trains annulés"]].rename(columns={
            "Date": "Month", "Service": "Service", ROUTE_COLS[1]: "Departure station", ROUTE_COLS[2]: "Arrival station",
            TARGET_COL: "Average arrival delay (min)", "Nombre de circulations prévues": "Scheduled trains", "Nombre de trains annulés": "Cancelled trains"})
        st.dataframe(view, hide_index=True, width="stretch")
        st.download_button("Download filtered observations", view.to_csv(index=False), "tardis_filtered.csv", "text/csv")

else:
    try:
        model, report, routes = artifact_cache()
    except Exception:
        logging.exception("Artifact loading failed")
        st.error("The matching model artifact could not be loaded. Install the pinned requirements and restore models/forecast.joblib, models/routes.csv and reports/metrics.json. Maintainers can rebuild with python -m src.train.")
        st.stop()
    selected = report["selected_model"]
    scores = report["test"][selected]
    if page == "Delay Prediction":
        st.info("2025 forecast replay · This model was trained through December 2024. Choose a known route and a month in the held-out year to replay a forecast made without using 2025 outcomes.")
        st.caption(f"Selected on 2024 validation MAE: {selected}. Only route identity and calendar are needed; no cancellations, observed journey durations or delay causes enter the model.")
        if selected == "Route historical mean":
            st.write("The selected baseline uses the historical average for each route. Its estimate is the same for every month of 2025; calendar effects are explored by the Random Forest candidate shown on the performance page.")
        service = st.selectbox("Service", sorted(routes.Service.unique()))
        subset = routes[routes.Service == service]
        departure = st.selectbox("Departure station", sorted(subset[ROUTE_COLS[1]].unique()))
        subset = subset[subset[ROUTE_COLS[1]] == departure]
        arrival = st.selectbox("Arrival station", sorted(subset[ROUTE_COLS[2]].unique()))
        with st.form("forecast"):
            month = st.selectbox("Forecast month · 2025", list(range(1, 13)), format_func=lambda n: date(2025, n, 1).strftime("%B %Y"))
            submitted = st.form_submit_button("Estimate monthly delay", type="primary")
        if submitted:
            try:
                prediction = predict_month(model, routes, service, departure, arrival, date(2025, month, 1))
                st.metric("Estimated mean arrival delay", f"{prediction:.2f} min")
                st.write(f"For {departure} → {arrival} in {date(2025, month, 1):%B %Y}, the estimated average across trains is {prediction:.2f} minutes relative to scheduled arrival.")
                st.caption(f"Held-out average absolute error: {scores['MAE']:.2f} min per route-month. This describes aggregate test error; it is not a confidence interval for this estimate.")
                history_count = int(subset.loc[subset[ROUTE_COLS[2]] == arrival, "training_months"].iloc[0])
                st.caption(f"Training support for this route: {history_count} eligible months.")
            except ValueError as error:
                st.error(str(error))
        st.warning("This is a historical demonstration, not a live journey planner. It cannot anticipate a specific incident, predict a particular train, or establish reliability for future years. No probability or individual prediction interval is claimed.")
    else:
        st.caption(f"Saved model: {selected} · Selection rule: {report['selection_rule']}.")
        cols = st.columns(3)
        for col, key in zip(cols, ["MAE", "RMSE", "R2"]):
            col.metric(key if key == "R2" else f"{key} (min)", f"{scores[key]:.3f}")
        st.write("MAE is the average size of an error. RMSE gives more weight to large misses. R² compares squared error with predicting the test mean; a value below zero means worse than that reference.")
        st.subheader("Measured comparison · untouched 2025 test set")
        st.dataframe(pd.DataFrame(report["test"]).T.rename_axis("Model").round(4), width="stretch")
        st.subheader("Protocol")
        st.write("Train on 2018–2023, select the candidate with the lowest MAE on 2024, then refit each candidate on 2018–2024 and evaluate once on 2025. All routes in a given month stay together. The saved pipeline is exactly the selected pipeline evaluated here; it is not refitted on the test year.")
        st.write("Random Forest uses 160 trees with bounded depth and leaf size. Its pipeline derives cyclical month features, imputes missing inputs and one-hot encodes categories. The route baseline uses training-only means with a global fallback for unknown routes.")
        pred = pd.read_csv(REPORT_PATH.with_name("predictions.csv"), parse_dates=["Date"])
        a, b = st.columns(2)
        with a:
            fig = px.scatter(pred, x="actual", y=selected, opacity=.35, title="Predicted vs observed · 2025", labels={"actual": "Observed average (min)", selected: "Predicted average (min)"})
            lo, hi = float(min(pred.actual.min(), pred[selected].min())), float(max(pred.actual.max(), pred[selected].max()))
            fig.add_shape(type="line", x0=lo, y0=lo, x1=hi, y1=hi, line=dict(color="#8a9e95", dash="dash"))
            st.plotly_chart(polish(fig), width="stretch")
        with b:
            pred["Error (min)"] = pred[selected] - pred.actual
            st.plotly_chart(polish(px.histogram(pred, x="Error (min)", nbins=40, title="Prediction errors · predicted minus observed")), width="stretch")
        pred["Absolute error (min)"] = pred["Error (min)"].abs()
        errors = pred.groupby("Date", as_index=False)["Absolute error (min)"].mean()
        st.plotly_chart(polish(px.line(errors, x="Date", y="Absolute error (min)", markers=True, title="Error through the test year", labels={"Date": "Month"})), width="stretch")
        st.warning("Monthly averages hide individual train variability. Source anomalies remain in the data and affect results. Historical route patterns cannot explain unexpected disruptions. One validation year and one test year do not establish stability across future periods.")
        with st.expander("Validation scores, data quality and reproducibility"):
            st.dataframe(pd.DataFrame(report["validation"]).T.round(4), width="stretch")
            st.json({k: report[k] for k in ["periods", "quality", "versions", "dataset_sha256", "model_sha256", "test_unseen_routes"]})
            st.download_button("Download evaluation report", json.dumps(report, indent=2), "tardis_metrics.json", "application/json")
