import unittest
import os
from unittest.mock import patch
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import ZIP_TEST_LAYERS

class TestLoadZipData(QgsPluginBaseTest):
    required_files = [ZIP_TEST_LAYERS]
    
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.MessageUtils.pushMessageBoxCritical')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getOpenFileName')
    def testPobierzWarstwyPochodneZip(self, mock_file_dialog, mock_critical):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Wczytywanie danych pochodnych z pliku ZIP")
        
        test_zip_path = os.path.join(self.data_dir, ZIP_TEST_LAYERS)
        mock_file_dialog.return_value = (test_zip_path, "ZIP")

        # Uruchomienie wczytywania
        self.dialog.pobierzWarstwyPochodne()

        # Weryfikacja wczytanych warstw
        self._verifyLoadedLayers()

        print(f" [WYNIK] Dane pochodne wczytane poprawnie \n")
        print('=' * 50)

    def _verifyLoadedLayers(self):
        """Sprawdza czy wymagane warstwy z pliku ZIP pojawiły się w projekcie."""
        project_layers = [l.name() for l in self.project.mapLayers().values()]
        input_cfg = self.module_const.INPUT_LAYERS
        
        expected = [
            input_cfg['drogi_lesne']['layer_name'],
            input_cfg['wydzielenia']['layer_name']
        ]

        for name in expected:
            self.assertIn(name, project_layers, f"Warstwa {name} nie została wczytana!")

if __name__ == "__main__":
    unittest.main()