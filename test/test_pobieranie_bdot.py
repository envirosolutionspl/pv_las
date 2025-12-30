import unittest
from unittest.mock import patch
from qgis.core import QgsProject
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_POWIATY

class TestBdotDownload(QgsPluginBaseTest):
    
    def setUp(self):
        super().setUp()
        # Przygotowanie warstwy powiatu
        self.dialog.powiaty = self.load_layer(GPKG_POWIATY, self.module_const.INPUT_LAYERS['powiaty']['layer_name'], self.module_const.INPUT_LAYERS['powiaty']['layer_name'])
        QgsProject.instance().addMapLayer(self.dialog.powiaty)

    @patch(f'{PLUGIN_NAME}.modules.dane_bdot_task.applyLayerStyle')
    def test_pobieranie_bdot_z_gpkg_input(self, mock_style):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Pobieranie danych BDOT10k")
        
        self.dialog.wczytajDaneBdot10k()
        task = getattr(self.dialog, 'bdot_task', None)
        self.wait_for_task(task)

        project = QgsProject.instance()
        l_drogi = project.mapLayersByName(self.module_const.LAYER_NAME_BDOT10K_DROGI)
        
        self.assertEqual(len(l_drogi), 1)
        cnt = l_drogi[0].featureCount()
        self.assertGreater(cnt, 0)

        print(f" [WYNIK] Dane pobrane poprawnie, niezerowa liczba obiektow \n")
        print('=' * 50)

if __name__ == "__main__":
    unittest.main()