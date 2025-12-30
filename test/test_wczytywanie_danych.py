import unittest
import os
from unittest.mock import patch
from qgis.core import QgsProject
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import ZIP_TEST_LAYERS

class TestLoadZipData(QgsPluginBaseTest):
    
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessageBoxCritical')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getOpenFileName')
    def test_pobierz_warstwy_pochodne_zip(self, mock_file_dialog, mock_critical):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Wczytywanie danych pochodnych z pliku ZIP")
        test_zip_path = os.path.join(self.data_dir, ZIP_TEST_LAYERS)
        mock_file_dialog.return_value = (test_zip_path, "ZIP")

        self.dialog.pobierzWarstwyPochodne()

        project_layer_names = [l.name() for l in QgsProject.instance().mapLayers().values()]
        input_layers_config = self.module_const.INPUT_LAYERS
        
        expected_names = [
            input_layers_config['drogi_lesne']['layer_name'],
            input_layers_config['wydzielenia']['layer_name']
        ]

        for name in expected_names:
            self.assertIn(name, project_layer_names, f"Warstwa {name} nie została wczytana!")

        print(f" [WYNIK] Dane pochodne wczytane poprawnie \n")
        print('=' * 50)

if __name__ == "__main__":
    unittest.main()