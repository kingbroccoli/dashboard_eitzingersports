import xml.etree.ElementTree as ET
import pandas as pd

# XML laden
tree = ET.parse('./xml_datei/Mietvelo.xml')
root = tree.getroot()

# Namespace definieren
ns = {'cr': 'urn:crystal-reports:schemas:report-detail'}

# Leere Liste für Teilnehmer mit Region
teilnehmer_liste = []

# Durch alle Gruppen der Ebene 1 (Bike-Typ/Region) iterieren
for group_level1 in root.findall('.//cr:Group[@Level="1"]', ns):
    # Extrahiere Fahrrad Typ und Region aus dem Text (z.B. "Mietrad Cube Attain/Axial (Carbon, Shimano 105) / MVCAM105")
    region_name = 'Unbekannt'
    
    for text in group_level1.findall('.//cr:Text', ns):
        if text.get('Name') == 'Text2':
            text_value = text.find('cr:TextValue', ns)
            if text_value is not None and text_value.text:
                full_text = text_value.text.strip()
                
                # Fahrrad Typ und Region trennen
                if '/' in full_text:
                    parts = [p.strip() for p in full_text.split('/')]
                    region_name = parts[-1]  # Letzter Teil nach dem Slash
    
    # Durch alle Details-Level-11-Elemente innerhalb dieser Gruppe iterieren
    for details in group_level1.findall('.//cr:Details[@Level="11"]', ns):
        # Extrahiere Teilnehmer, Datum, ServiceType
        teilnehmer = None
        datum_von = None
        datum_bis = None
        rahmengroesse = 'Unbekannt'
        
        for field in details.findall('.//cr:Field', ns):
            field_name = field.get('Name')
            formatted_value = field.find('cr:FormattedValue', ns)
            value = formatted_value.text.strip() if formatted_value is not None and formatted_value.text else ''
            
            if field_name == 'Teilnehmer1':
                # Teilnehmername aufteilen (z.B. "Frau Bruggmann/Doris")
                if '/' in value:
                    nachname, vorname = value.split('/', 1)
                    teilnehmer = {'Nachname': nachname, 'Vorname': vorname}
                else:
                    teilnehmer = {'Nachname': value, 'Vorname': ''}
            
            elif field_name == 'DATUMVON1':
                datum_von = value
            
            elif field_name == 'DATUMBIS1':
                datum_bis = value
            
            elif field_name == 'ServiceType1':
                # Extrahiere nur den Teil vor dem ersten Komma (z.B. "Rahmengrösse 53")
                if ',' in value:
                    rahmengroesse = value.split(',', 1)[0].strip()
                else:
                    rahmengroesse = value
        
        # Wenn alle Daten vorhanden sind, füge sie zur Liste hinzu
        if teilnehmer and datum_von and datum_bis and rahmengroesse:
            teilnehmer['Datum_von'] = datum_von
            teilnehmer['Datum_bis'] = datum_bis
            teilnehmer['Rahmengrösse'] = rahmengroesse
            teilnehmer['Region'] = region_name
            teilnehmer_liste.append(teilnehmer)

# DataFrame erstellen und anzeigen
df = pd.DataFrame(teilnehmer_liste)
print(df[['Nachname', 'Vorname', 'Datum_von', 'Datum_bis', 'Rahmengrösse', 'Region']].to_string(index=False))