import unittest
from unittest.mock import patch
from qgis.core import QgsProject
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_ANALIZA, EXPECTED_FEATURE_COUNT

class TestAnaliza(QgsPluginBaseTest):
    
    def setUp(self):
        super().setUp()
        gpkg = GPKG_ANALIZA
        
        self.dialog.wydzielenia = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['wydzielenia']['layer_name'], self.module_const.INPUT_LAYERS['wydzielenia']['layer_name'])
        self.dialog.wydzielenia_opisy = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['wydzielenia_opisy']['layer_name'], self.module_const.INPUT_LAYERS['wydzielenia_opisy']['layer_name'])
        self.dialog.oddzialy = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['oddzialy']['layer_name'], self.module_const.INPUT_LAYERS['oddzialy']['layer_name'])
        self.dialog.drogi_lesne = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['drogi_lesne']['layer_name'], self.module_const.INPUT_LAYERS['drogi_lesne']['layer_name'])

        self.drogi_bdot = self.load_layer(gpkg, self.module_const.LAYER_NAME_BDOT10K_DROGI, self.module_const.LAYER_NAME_BDOT10K_DROGI)
        self.linie_bdot = self.load_layer(gpkg, self.module_const.LAYER_NAME_BDOT10K_LINIE, self.module_const.LAYER_NAME_BDOT10K_LINIE)
        
        QgsProject.instance().addMapLayers([
            self.dialog.wydzielenia, 
            self.drogi_bdot, 
            self.linie_bdot
        ])
        
        self.dialog.mapa_bazowa = self.dialog.wydzielenia

    @patch(f'{PLUGIN_NAME}.modules.analiza_task.applyLayerStyle')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def test_analiza_wykonanie(self, mock_push, mock_style):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Analiza danych")
        
        self.dialog.analizaData()
        task = getattr(self.dialog, 'analiza_task', None)
        self.wait_for_task(task)

        project = QgsProject.instance()
        lyr_obszary = project.mapLayersByName(self.module_const.NAME_LAYER_OBSZARY)
        
        # Sprawdzenia (Asserty)
        self.assertEqual(len(lyr_obszary), 1)
        count = lyr_obszary[0].featureCount()
        self.assertEqual(count, EXPECTED_FEATURE_COUNT)

        print(f" [WYNIK] Sukses. Poprawna liczba obiektow \n")
        print('=' * 50)

if __name__ == "__main__":
    unittest.main()