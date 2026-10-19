# Dashboard guide

Use Python 3.12 and install `requirements.txt`, then run:

```bash
python -m streamlit run tardis_dashboard.py
```

Use the sidebar to navigate Overview, Data Explorer, Delay Prediction and Model
Performance. Explorer filters update all its plots and its downloadable table.
Selecting no years or services displays an explicit empty state. Station selections
in Prediction are restricted to directed routes seen before 2025. The forecast
button returns a monthly mean in minutes; the selected route baseline returns the
same estimate across months for that route. This is a 2025 forecast replay.

The performance page shows measured results with a chronological protocol and
source-quality limitations. Data are cached and the model is loaded from disk;
training is a separate maintainer command, `python -m src.train`.
See the root README for setup, provenance, results and deployment.
