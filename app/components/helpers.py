"""Pure filtering functions shared by the UI and its regression tests."""

def filter_data(df, years, services, departure="All stations", arrival="All stations"):
    mask = df.Year.isin(years) & df.Service.isin(services)
    if departure != "All stations":
        mask &= df["Gare de départ"].eq(departure)
    if arrival != "All stations":
        mask &= df["Gare d'arrivée"].eq(arrival)
    return df.loc[mask].copy()
