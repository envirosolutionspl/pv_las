
import xlsxwriter
from ..constants import EXCEL_TABLE_STYLE, EXCEL_REPORT_COLUMNS


class GenerujRaport():
    """Klasa generująca raport
    """

    def tworzTabele(self, nazwa_pliku, obszary, drogi, linie, nazwa_nadl):
        """Tworzy tabelę excela.
        """
        # Mapowanie danych po numerze obszaru, aby uniknąć błędów indeksacji
        map_drogi = {f[0]: (f[1], f[2]) for f in drogi.getFeatures()}
        map_linie = {f[0]: (f[1], f[2]) for f in linie.getFeatures()}

        dane = []
        for feature in obszary.getFeatures():
            nr = feature[0]
            # Pobieramy dane o drodze lub dajemy wartości domyślne
            odl_droga, rodz_droga = map_drogi.get(nr, (None, "Nie znaleziono"))
            # Pobieramy dane o linii lub dajemy wartości domyślne
            odl_linia, rodz_linia = map_linie.get(nr, (None, "Nie znaleziono"))

            dane.append([
                nr,
                feature[1], # adres leśny
                feature[2], # powierzchnia
                odl_droga,
                rodz_droga,
                odl_linia,
                rodz_linia
            ])

        if not dane:
            return

        workbook = xlsxwriter.Workbook(nazwa_pliku)
        worksheet = workbook.add_worksheet('Nadleśnictwo {}'.format(nazwa_nadl))

        # styl tabeli
        last_row = len(dane) + 1
        worksheet.add_table('A1:G{}'.format(last_row), {
            'data': dane, 
            'autofilter': False, 
            'style': EXCEL_TABLE_STYLE,
            'banded_rows': 0, 
            'banded_columns': 1, 
            'columns': EXCEL_REPORT_COLUMNS
        })

        worksheet.autofit()
        workbook.close()
