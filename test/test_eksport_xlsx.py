import os
import pandas as pd
from unittest.mock import patch
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_EKSPORT, FILENAME_REPORT_XLSX
import warnings

class TestEksportExcel(QgsPluginBaseTest):

    def setUp(self):
        super().setUp()

        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            module="openpyxl"
        )

        gpkg = GPKG_EKSPORT
        
        self.lyr_obszary = self.loadLayer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.lyr_linie = self.loadLayer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.lyr_drogi = self.loadLayer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        
        self.dialog.nadlesnictwo = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'], self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'])
        
        self.project.addMapLayers([
            self.lyr_obszary, self.lyr_linie, self.lyr_drogi, self.dialog.nadlesnictwo
        ])

        self.output_xlsx = os.path.join(self.data_dir, FILENAME_REPORT_XLSX)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.openFile')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.ZapiszXLSX.zapiszExcel')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def testGenerujRaportProces(self, mock_push, mock_save, mock_open):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Eksport do Excela")

        mock_save.return_value = self.output_xlsx

        # Uruchomienie eksportu
        self.dialog.generujRaport()

        # Wczytanie pliku do weryfikacji
        self.assertTrue(os.path.exists(self.output_xlsx), "Plik Excel nie został utworzony!")
        df = pd.read_excel(self.output_xlsx)
        
        # Weryfikacja liczby wierszy
        self._verifyRowCount(df)

        # Weryfikacja nagłówków
        self._verifyHeaders(df)

        # Weryfikacja przykładowych danych
        self._verifyDataMapping(df)

        print(f" [WYNIK] Raport Excel poprawny, liczba wierszy i nagłówki OK \n")
        print("=" * 50)

    def _verifyRowCount(self, df):
        """Sprawdza czy liczba wierszy w Excelu zgadza się z liczbą obiektów na warstwie."""
        expected = self.lyr_obszary.featureCount()
        actual = len(df)
        self.assertEqual(actual, expected, f"Błędna liczba wierszy! Jest {actual}, oczekiwano {expected}.")

    def _verifyHeaders(self, df):
        """Sprawdza poprawność nagłówków kolumn w pliku Excel."""
        expected = [col['header'] for col in self.module_const.EXCEL_REPORT_COLUMNS]
        actual = list(df.columns)
        self.assertEqual(actual, expected, "Nagłówki w Excelu są niepoprawne")

    def _verifyDataMapping(self, df):
        """Sprawdza poprawność mapowania danych (przykładowy rekord)."""
        self.assertEqual(df.iloc[0, 0], 1, "Błąd mapowania danych - ID pierwszego obszaru się nie zgadza")

    def tearDown(self):
        if os.path.exists(self.output_xlsx):
            try:
                os.remove(self.output_xlsx)
            except:
                pass
        super().tearDown()