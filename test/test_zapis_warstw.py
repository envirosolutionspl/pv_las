import os
import gc
import shutil
from unittest.mock import patch, MagicMock
from qgis.core import QgsVectorLayer
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_EKSPORT, DIR_SHP_TEMP

class TestEksportSHP(QgsPluginBaseTest):
    required_files = [GPKG_EKSPORT]

    def setUp(self):
        super().setUp()
        gpkg = GPKG_EKSPORT
        
        self.lyr_obszary = self.loadLayer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.lyr_linie = self.loadLayer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.lyr_drogi = self.loadLayer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        
        self.project.addMapLayers([self.lyr_obszary, self.lyr_linie, self.lyr_drogi])

        self.output_dir = os.path.join(self.data_dir, DIR_SHP_TEMP)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.openFile')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def testZapiszWarstwyWszystkie(self, mock_push, mock_save_dialog, mock_open):
        print("\n" + "=" * 50)
        print("\n [TEST] Eksport warstw SHP")

        main_shp = os.path.join(self.output_dir, "obszary.shp")
        mock_save_dialog.return_value = (main_shp, "*.shp")

        # Uruchomienie eksportu
        self.dialog.zapiszWarstwy()

        # Weryfikacja wynikowych plików SHP
        expected_files = [
            main_shp,
            os.path.join(self.output_dir, self.module_const.FILENAME_LAYER_LINIE),
            os.path.join(self.output_dir, self.module_const.FILENAME_LAYER_DROGI)
        ]
        self._verifyShapefiles(expected_files)

        print(f" [WYNIK] Poprawnie zweryfikowano 3 pliki SHP. \n")
        print("=" * 50)

    def _verifyShapefiles(self, file_paths):
        """Sprawdza istnienie i poprawność plików SHP."""
        for path in file_paths:
            self.assertTrue(os.path.exists(path), f"Plik {path} nie został utworzony!")
            
            check_lyr = QgsVectorLayer(path, "temporary_check", "ogr")
            self.assertTrue(check_lyr.isValid(), f"Plik SHP jest nieprawidłowy: {path}")
            
            check_lyr = None 

    def tearDown(self):
        """Sprzątanie po eksporcie SHP."""
        self.project.removeAllMapLayers()
        gc.collect() 
        
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir, ignore_errors=True)
            
        super().tearDown()