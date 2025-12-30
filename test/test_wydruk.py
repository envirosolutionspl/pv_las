import os
from unittest.mock import patch, MagicMock
from qgis.core import (
    QgsProject, 
    QgsLayoutItemLabel, 
    QgsLayoutItemMap, 
    QgsLayoutItemPicture, 
    QgsLayoutItemLegend, 
    QgsLayoutItemScaleBar
)
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_EKSPORT, FILENAME_WYDRUK_PDF

class TestEksportWydruk(QgsPluginBaseTest):

    def setUp(self):
        super().setUp()
        gpkg = GPKG_EKSPORT
        
        self.dialog.obszary_layer = self.load_layer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.dialog.linie_layer = self.load_layer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.dialog.drogi_layer = self.load_layer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        self.dialog.nadlesnictwo = self.load_layer(gpkg, self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'], self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'])
    
        QgsProject.instance().addMapLayers([
            self.dialog.obszary_layer, 
            self.dialog.linie_layer, 
            self.dialog.drogi_layer, 
            self.dialog.nadlesnictwo
        ])

        self.output_img = os.path.join(self.data_dir, FILENAME_WYDRUK_PDF)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.openFile')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.pushMessage')
    def test_generuj_wydruk_kompletny(self, mock_push, mock_save, mock_open):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Weryfikacja zawartości wydruku")

        mock_save.return_value = (self.output_img, "pdf")

        # Uruchomienie generatora
        self.dialog.generujWydruk()

        # Pobranie layoutu
        layout_manager = QgsProject.instance().layoutManager()
        layouts = layout_manager.printLayouts()
        self.assertGreater(len(layouts), 0, "Nie utworzono layoutu!")
        
        layout = layouts[0]
        items = layout.items()

        # Weryfikacja mapy
        maps = [i for i in items if isinstance(i, QgsLayoutItemMap)]
        self.assertEqual(len(maps), 1)
        
        map_item = maps[0]
        map_layer_names = [l.name() for l in map_item.layers()]
        
        expected_results = [
            self.module_const.NAME_LAYER_OBSZARY,
            self.module_const.NAME_LAYER_LINIE,
            self.module_const.NAME_LAYER_DROGI
        ]
        
        for name in expected_results:
            self.assertIn(name, map_layer_names, f"Warstwa {name} nie została dodana do mapy w wydruku")

        # Weryfikacja legendy
        legends = [i for i in items if isinstance(i, QgsLayoutItemLegend)]
        self.assertEqual(len(legends), 1, "Brak legendy")
        
        legend = legends[0]
        self.assertEqual(legend.linkedMap(), map_item, "Legenda nie jest powiązana z mapą")
        
        nodes = legend.model().rootGroup().findLayers()
        legend_layer_names = []
        for n in nodes:
            if n is not None:
                legend_layer_names.append(n.name())
            else:
                print(" [DEBUG] Znaleziono pusty węzeł w legendzie")
        
        for name in expected_results:
            self.assertIn(name, legend_layer_names, f"Warstwa {name} nie widnieje w legendzie")

        # Weryfikacja tytułu
        labels = [i for i in items if isinstance(i, QgsLayoutItemLabel)]
        
        attr_name = self.module_const.LAYOUT_CONFIG['TITLE']['ATTR_NAME']
        nazwa_nadl = self.module_utils.pobierzNazweZWarstwy(self.dialog.nadlesnictwo, attr_name, self.iface_mock)
        
        oczekiwany_tytul = self.module_const.LAYOUT_CONFIG['TITLE']['TEXT_TEMPLATE'].format(nazwa_nadl)
        
        has_correct_title = any(l.text() == oczekiwany_tytul for l in labels)
        self.assertTrue(has_correct_title, f"Brak poprawnego tytułu. Oczekiwano: '{oczekiwany_tytul}'")
        
        # Weryfikacja obrazów
        pictures = [i for i in items if isinstance(i, QgsLayoutItemPicture)]
        self.assertEqual(len(pictures), 3, "Brak logotypów lub strzałki północy (powinny być 3 obrazy)")

        print(f" [WYNIK] Wydruk kompletny: Obszary, Linie i Drogi są na mapie i w legendzie, tytuły są poprawne, obrazy są na miejscach. \n")
        print("=" * 50)

    def tearDown(self):
        if os.path.exists(self.output_img):
            try: os.remove(self.output_img)
            except: pass
        QgsProject.instance().layoutManager().clear()
        super().tearDown()