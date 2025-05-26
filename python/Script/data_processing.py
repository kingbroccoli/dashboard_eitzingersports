# data_processing.py
import pandas as pd

def expand_dates(df):
    """Erweitert die Daten auf tägliche Einträge"""
    expanded = []
    for _, row in df.iterrows():
        dates = pd.date_range(
            start=pd.to_datetime(row['Datum_von'], format='%d.%m.%Y'),
            end=pd.to_datetime(row['Datum_bis'], format='%d.%m.%Y')
        )
        for date in dates:
            expanded.append({
                'Datum': date,
                'Zugang': 1 if date == dates[0] else 0,
                'Abgang': 1 if date == dates[-1] else 0,
                'Bestand': 1
            })
    return pd.DataFrame(expanded).groupby('Datum').sum().reset_index()