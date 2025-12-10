
import xlsxwriter


class GenerujRaport():
    """Klasa generująca raport
    """

    def tworzTabele(self, nazwa_pliku, obszary, drogi, linie, nazwa_nadl):
        """Tworzy tabelę excela.

        Args:
            nazwa_pliku (str): wybrana ścieżka eksportu
            obszary (QgsVectorLayer): warstwa z wyznaczonymi obszarami
            drogi (QgsVectorLayer): warstwa z najbliższymi drogami
            linie (QgsVectorLayer): warstwa z najbliższymi liniami energetycznymi
            nazwa_nadlesnictwa (str): nazwa nadleśnictwa
        """
        numery_obszarow = [feature[0] for feature in obszary.getFeatures()]
        adresy_lesne = [feature[1] for feature in obszary.getFeatures()]
        powierzchnie = [feature[2] for feature in obszary.getFeatures()]
        odleglosci_od_drog =  [feature[1] for feature in drogi.getFeatures()]
        rodzaje_drog =  [feature[2] for feature in drogi.getFeatures()]
        odleglosci_od_linii=  [feature[1] for feature in linie.getFeatures()]
        rodzaje_linii =  [feature[2] for feature in linie.getFeatures()]

        dane = [
                    [
                    numery_obszarow[i], 
                    adresy_lesne[i],
                    powierzchnie[i],  
                    odleglosci_od_drog[i],
                    rodzaje_drog[i],
                    odleglosci_od_linii[i],
                    rodzaje_linii[i]
                    ] 
                    for i in range(0,len(numery_obszarow))
                ]

        workbook = xlsxwriter.Workbook(nazwa_pliku)
        worksheet = workbook.add_worksheet('Nadleśnictwo {}'.format(nazwa_nadl))

        worksheet.add_table('A1:G{}'.format(len(numery_obszarow)+1), {'data': dane, 'autofilter': False, 'style': 'Table Style Medium 4','banded_rows': 0, 'banded_columns': 1, 'columns': [
            {'header': 'NR OBSZARU'},
            {'header': 'ADRES/Y LEŚNY/E'},
            {'header': 'POWIERZCHNIA OBSZARU (HA)'},
            {'header': 'ODLEGŁOŚĆ OD DROGI (M)'},
            {'header': 'RODZAJ DROGI'},
            {'header': 'ODLEGŁOŚĆ OD LINII ENERGETYCZNEJ (M)'},
            {'header': 'RODZAJ LINII ENERGETYCZNEJ'},
        ]})
        worksheet.autofit()
        workbook.close()
