import os
import pandas as pd
from unittest.mock import patch
from qgis.core import QgsProject
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
        
        self.lyr_obszary = self.load_layer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.lyr_linie = self.load_layer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.lyr_drogi = self.load_layer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        
        self.dialog.nadlesnictwo = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'], self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'])
        
        QgsProject.instance().addMapLayers([
            self.lyr_obszary, self.lyr_linie, self.lyr_drogi, self.dialog.nadlesnictwo
        ])

        self.output_xlsx = os.path.join(self.data_dir, FILENAME_REPORT_XLSX)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.openFile')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.ZapiszXLSX.zapiszExcel')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def test_generuj_raport_proces(self, mock_push, mock_save, mock_open):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Eksport do Excela")

        mock_save.return_value = self.output_xlsx

        self.dialog.generujRaport()

        self.assertTrue(os.path.exists(self.output_xlsx), "Plik Excel nie został utworzony!")

        df = pd.read_excel(self.output_xlsx)
        
        row_numbers = self.lyr_obszary.featureCount()

        self.assertEqual(len(df), row_numbers, f"Błędna liczba wierszy! Jest {len(df)}, oczekiwano {row_numbers}.")

        expected_headers = [col['header'] for col in self.module_const.EXCEL_REPORT_COLUMNS]
        actual_headers = list(df.columns)
        self.assertEqual(actual_headers, expected_headers, "Nagłówki w Excelu są niepoprawne")

        self.assertEqual(df.iloc[0, 0], 1, "Błąd mapowania danych - Nr obszaru się nie zgadza")

        print(f" [WYNIK] Raport Excel poprawny, liczba wierszy i nagłówki OK \n")
        print("=" * 50)

    def tearDown(self):
        if os.path.exists(self.output_xlsx):
            try:
                os.remove(self.output_xlsx)
            except:
                pass
        super().tearDown()