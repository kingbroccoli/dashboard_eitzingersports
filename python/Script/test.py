import xml.etree.ElementTree as ET
import pandas as pd

# XML laden
tree = ET.parse('./xml_datei/report.xml')
root = tree.getroot()

# Namespace definieren
ns = {'cr': 'urn:crystal-reports:schemas:report-detail'}

# Leere Liste für Teilnehmer mit Region
teilnehmer_liste = []

# Durch alle Gruppen der Ebene 2 (Region) iterieren
for group_level2 in root.findall('.//cr:Group[@Level="2"]', ns):
    # Extrahiere Region aus der Gruppe Level=2
    region_name = None
    for field in group_level2.findall('.//cr:Field', ns):
        if field.get('Name') == 'RegionName1':
            formatted_value = field.find('cr:FormattedValue', ns)
            region_name = formatted_value.text.strip() if formatted_value is not None else 'Unbekannt'
    
    # Durch alle Details-Level-10-Elemente innerhalb dieser Region iterieren
    for details in group_level2.findall('.//cr:Details[@Level="10"]', ns):
        # Extrahiere Teilnehmer, Datum, Geschwindigkeitsgruppe
        teilnehmer = None
        datum_von = None
        datum_bis = None
        service_type = None
        
        for field in details.findall('.//cr:Field', ns):
            field_name = field.get('Name')
            formatted_value = field.find('cr:FormattedValue', ns)
            value = formatted_value.text.strip() if formatted_value is not None and formatted_value.text else ''
            
            if field_name == 'Teilnehmer1':
                # Teilnehmername aufteilen (z.B. "Herr Rutz/Markus Christian")
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
                service_type = value
        
        # Wenn alle Daten vorhanden sind, füge sie zur Liste hinzu
        if teilnehmer and datum_von and datum_bis and service_type and region_name:
            teilnehmer['Datum_von'] = datum_von
            teilnehmer['Datum_bis'] = datum_bis
            teilnehmer['ServiceType'] = service_type
            teilnehmer['Region'] = region_name
            teilnehmer_liste.append(teilnehmer)

# DataFrame erstellen und anzeigen
df = pd.DataFrame(teilnehmer_liste)
print(df.to_string(index=False))