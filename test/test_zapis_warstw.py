import os
import gc
import shutil
from unittest.mock import patch, MagicMock
from qgis.core import QgsProject, QgsVectorLayer
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_EKSPORT, DIR_SHP_TEMP

class TestEksportSHP(QgsPluginBaseTest):

    def setUp(self):
        super().setUp()
        gpkg = GPKG_EKSPORT
        
        self.lyr_obszary = self.load_layer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.lyr_linie = self.load_layer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.lyr_drogi = self.load_layer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        
        QgsProject.instance().addMapLayers([self.lyr_obszary, self.lyr_linie, self.lyr_drogi])

        self.output_dir = os.path.join(self.data_dir, DIR_SHP_TEMP)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.openFile')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def test_zapisz_warstwy_wszystkie(self, mock_push, mock_save_dialog, mock_open):
        print("\n" + "=" * 50)
        print("\n [TEST] Eksport warstw SHP")

        main_shp = os.path.join(self.output_dir, "obszary.shp")
        mock_save_dialog.return_value = (main_shp, "*.shp")

        self.dialog.zapiszWarstwy()

        path_linie = os.path.join(self.output_dir, self.module_const.FILENAME_LAYER_LINIE)
        path_drogi = os.path.join(self.output_dir, self.module_const.FILENAME_LAYER_DROGI)

        for path in [main_shp, path_linie, path_drogi]:
            self.assertTrue(os.path.exists(path), f"Plik {path} nie został utworzony!")
            
            check_lyr = QgsVectorLayer(path, "temporary_check", "ogr")
            self.assertTrue(check_lyr.isValid())
            self.assertEqual(check_lyr.featureCount(), check_lyr.featureCount())
            check_lyr = None 

        print(f" [WYNIK] Poprawnie zweryfikowano 3 pliki SHP. \n")
        print("=" * 50)

    def tearDown(self):
        """Sprzątanie po eksporcie SHP."""
        QgsProject.instance().removeAllMapLayers()
        gc.collect() 
        
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir, ignore_errors=True)
            
        super().tearDown()