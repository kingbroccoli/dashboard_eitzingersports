import pandas as pd
from datetime import timedelta

# Beispiel-Daten
data = {
    'Beschreibung': [
        'Rennvelo Grösse 56 Shimano 105',
        'Rennvelo Grösse 56 Shimano 105',
        'Rennvelo Grösse 50 Shimano Ultegra',
    ],
    'Von': ['22.09.2024', '25.09.2024', '26.09.2024'],
    'Bis': ['28.09.2024', '30.09.2024', '01.10.2024']
}

df = pd.DataFrame(data)

# Datum in datetime umwandeln
df['Von'] = pd.to_datetime(df['Von'], format='%d.%m.%Y')
df['Bis'] = pd.to_datetime(df['Bis'], format='%d.%m.%Y')

# Alle Tage zwischen "Von+1" und "Bis-1" pro Buchung
records = []
for _, row in df.iterrows():
    start = row['Von'] + timedelta(days=1)
    end = row['Bis'] - timedelta(days=1)
    if start <= end:
        for date in pd.date_range(start, end):
            records.append({
                'Beschreibung': row['Beschreibung'],
                'Datum': date
            })

# Neues DataFrame
usage_df = pd.DataFrame(records)

# Pivot-Tabelle: Zeilen = Beschreibung, Spalten = Datum, Werte = Anzahl
pivot = usage_df.pivot_table(index='Beschreibung', columns='Datum', aggfunc='size', fill_value=0)

# Optional: Spalten als Datum formatieren
pivot.columns = pivot.columns.strftime('%d.%m.%Y')

# Ergebnis anzeigen
print(pivot)
