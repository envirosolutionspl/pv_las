import unittest
from unittest.mock import patch
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_ANALIZA, EXPECTED_FEATURE_COUNT

class TestAnaliza(QgsPluginBaseTest):
    
    def setUp(self):
        super().setUp()
        gpkg = GPKG_ANALIZA
        
        self.dialog.wydzielenia = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['wydzielenia']['layer_name'], self.module_const.INPUT_LAYERS['wydzielenia']['layer_name'])
        self.dialog.wydzielenia_opisy = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['wydzielenia_opisy']['layer_name'], self.module_const.INPUT_LAYERS['wydzielenia_opisy']['layer_name'])
        self.dialog.oddzialy = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['oddzialy']['layer_name'], self.module_const.INPUT_LAYERS['oddzialy']['layer_name'])
        self.dialog.drogi_lesne = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['drogi_lesne']['layer_name'], self.module_const.INPUT_LAYERS['drogi_lesne']['layer_name'])

        self.drogi_bdot = self.loadLayer(gpkg, self.module_const.LAYER_NAME_BDOT10K_DROGI, self.module_const.LAYER_NAME_BDOT10K_DROGI)
        self.linie_bdot = self.loadLayer(gpkg, self.module_const.LAYER_NAME_BDOT10K_LINIE, self.module_const.LAYER_NAME_BDOT10K_LINIE)
        
        self.project.addMapLayers([
            self.dialog.wydzielenia, 
            self.drogi_bdot, 
            self.linie_bdot
        ])
        
        self.dialog.mapa_bazowa = self.dialog.wydzielenia
        
    @patch(f'{PLUGIN_NAME}.modules.analiza_task.applyLayerStyle')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def testAnalizaWykonanie(self, mock_push, mock_style):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Analiza danych")
        
        self.dialog.analizaData()
        task = getattr(self.dialog, 'analiza_task', None)
        self.waitForTask(task)

        lyr_obszary = self.project.mapLayersByName(self.module_const.NAME_LAYER_OBSZARY)
        
        # Sprawdzenie czy warstwa obszary została stworzona
        self.assertEqual(len(lyr_obszary), 1)
        
        # Sprawdzenie czy liczba obiektow jest poprawna
        count = lyr_obszary[0].featureCount()
        self.assertEqual(count, EXPECTED_FEATURE_COUNT)

        print(f" [WYNIK] Sukses. Poprawna liczba obiektow \n")
        print('=' * 50)

if __name__ == "__main__":
    unittest.main()