# dashboard.py (Streamlit oder Dash)
import streamlit as st
import pandas as pd
from xml_script import MietveloParser
from data_processing import expand_dates


def check_password():
    def password_entered():
        if st.session_state["password"] == "geheim123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Passwort nicht im Speicher lassen
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Passwort", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Passwort", type="password", on_change=password_entered, key="password")
        st.error("Falsches Passwort")
        st.stop()

# Vor App-Inhalt
check_password()

# Danach kommt deine eigentliche App
st.write("✅ Willkommen in der App!")

# XML-Daten laden
mietvelo_parser = MietveloParser('./xml_datei/Mietvelo.xml', {'cr': 'urn:crystal-reports:schemas:report-detail'})
mietvelo_parser.parse()
mietvelo_df = mietvelo_parser.to_dataframe()

# Datum konvertieren
mietvelo_df['Datum_von'] = pd.to_datetime(mietvelo_df['Datum_von'], format='%d.%m.%Y')
mietvelo_df['Datum_bis'] = pd.to_datetime(mietvelo_df['Datum_bis'], format='%d.%m.%Y')

# Tägliche Einträge generieren
records = []
for _, row in mietvelo_df.iterrows():
    dates = pd.date_range(start=row['Datum_von'], end=row['Datum_bis'])
    for date in dates:
        records.append({
            'Datum': date,
            'Rahmengrösse': row['Rahmengrösse'],
            'Region': row['Region'],
            'Anzahl': 1
        })

# DataFrame erstellen
daily_usage = pd.DataFrame(records).groupby(['Datum', 'Rahmengrösse', 'Region']).sum().reset_index()

# Region-Filter
st.sidebar.header("Filter")
regions = daily_usage['Region'].unique()
selected_region = st.sidebar.selectbox("Region auswählen", options=regions)

# Daten filtern
filtered_data = daily_usage[daily_usage['Region'] == selected_region]

# Pivot-Tabelle erstellen
pivot = filtered_data.pivot_table(
    index='Rahmengrösse',
    columns='Datum',
    values='Anzahl',
    aggfunc='sum',
    fill_value=0
)

# Spaltenformatierung
pivot.columns = pivot.columns.strftime('%d.%m.%Y')

# Tabelle anzeigen
st.subheader(f"Tägliche Auslastung (Region: {selected_region})")
st.dataframe(pivot)

