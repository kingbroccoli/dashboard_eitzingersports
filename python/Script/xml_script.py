# xml_script.py
import xml.etree.ElementTree as ET
import pandas as pd
from abc import ABC, abstractmethod

class XMLParser(ABC):
    def __init__(self, file_path, namespace):
        self.file_path = file_path
        self.ns = namespace
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        self.data = []

    @abstractmethod
    def parse(self):
        """Extrahiert Daten aus dem XML"""
        pass

    def to_dataframe(self):
        """Konvertiert die Daten in ein DataFrame"""
        return pd.DataFrame(self.data)

    def save_csv(self, filename):
        """Speichert die Daten als CSV"""
        self.to_dataframe().to_csv(filename, index=False, sep=';', encoding='utf-8-sig')

class NiveauParser(XMLParser):
    def parse(self):
        for group_level2 in self.root.findall('.//cr:Group[@Level="2"]', self.ns):
            region_name = self._extract_region(group_level2)
            self._extract_participants(group_level2, region_name)

    def _extract_region(self, group):
        for field in group.findall('.//cr:Field', self.ns):
            if field.get('Name') == 'RegionName1':
                formatted_value = field.find('cr:FormattedValue', self.ns)
                return formatted_value.text.strip() if formatted_value is not None else 'Unbekannt'
        return 'Unbekannt'

    def _extract_participants(self, group, region):
        for details in group.findall('.//cr:Details[@Level="10"]', self.ns):
            participant = {}
            datum_von = None
            datum_bis = None
            service_type = None
            
            for field in details.findall('.//cr:Field', self.ns):
                field_name = field.get('Name')
                formatted_value = field.find('cr:FormattedValue', self.ns)
                value = formatted_value.text.strip() if formatted_value is not None and formatted_value.text else ''
                
                if field_name == 'Teilnehmer1':
                    if '/' in value:
                        nachname, vorname = value.split('/', 1)
                        participant = {'Nachname': nachname, 'Vorname': vorname}
                    else:
                        participant = {'Nachname': value, 'Vorname': ''}
                
                elif field_name == 'DATUMVON1':
                    datum_von = value
                
                elif field_name == 'DATUMBIS1':
                    datum_bis = value
                
                elif field_name == 'ServiceType1':
                    service_type = value

            if participant and datum_von and datum_bis and service_type:
                participant['Datum_von'] = datum_von
                participant['Datum_bis'] = datum_bis
                participant['ServiceType'] = service_type
                participant['Region'] = region
                self.data.append(participant)

class MietveloParser(XMLParser):
    def parse(self):
        for group_level1 in self.root.findall('.//cr:Group[@Level="1"]', self.ns):
            region_name = self._extract_region(group_level1)
            self._extract_participants(group_level1, region_name)

    def _extract_region(self, group):
        for text in group.findall('.//cr:Text', self.ns):
            if text.get('Name') == 'Text2':
                text_value = text.find('cr:TextValue', self.ns)
                if text_value is not None and text_value.text:
                    full_text = text_value.text.strip()
                    if '/' in full_text:
                        return full_text.split('/')[-1].strip()
        return 'Unbekannt'

    def _extract_participants(self, group, region):
        for details in group.findall('.//cr:Details[@Level="12"]', self.ns):
            participant = {}
            datum_von = None
            datum_bis = None
            rahmengroesse = 'Unbekannt'
            
            for field in details.findall('.//cr:Field', self.ns):
                field_name = field.get('Name')
                formatted_value = field.find('cr:FormattedValue', self.ns)
                value = formatted_value.text.strip() if formatted_value is not None and formatted_value.text else ''
                
                if field_name == 'Teilnehmer1':
                    if '/' in value:
                        nachname, vorname = value.split('/', 1)
                        participant = {'Nachname': nachname, 'Vorname': vorname}
                    else:
                        participant = {'Nachname': value, 'Vorname': ''}
                
                elif field_name == 'DATUMVON1':
                    datum_von = value
                
                elif field_name == 'DATUMBIS1':
                    datum_bis = value
                
                elif field_name == 'ServiceType1':
                    if ',' in value:
                        rahmengroesse = value.split(',')[0].strip()
                    else:
                        rahmengroesse = value

            if participant and datum_von and datum_bis:
                participant['Datum_von'] = datum_von
                participant['Datum_bis'] = datum_bis
                participant['Rahmengrösse'] = rahmengroesse
                participant['Region'] = region
                self.data.append(participant)

if __name__ == "__main__":
    # Teste den Parser direkt im XML-Skript
    mietvelo_parser = MietveloParser('./xml_datei/Mietvelo.xml', {'cr': 'urn:crystal-reports:schemas:report-detail'})
    mietvelo_parser.parse()
    mietvelo_df = mietvelo_parser.to_dataframe()
    print("Mietvelo-Daten:")
    print(mietvelo_df.head())  # Zeige die ersten Zeilen zur Überprüfung