import os
from unittest.mock import patch, MagicMock
from qgis.core import (
    QgsLayoutItemLabel, 
    QgsLayoutItemMap, 
    QgsLayoutItemPicture, 
    QgsLayoutItemLegend, 
    QgsLayoutItemScaleBar
)
from .base_test import QgsPluginBaseTest, PLUGIN_NAME
from .constants import GPKG_EKSPORT, FILENAME_WYDRUK_PDF

class TestEksportWydruk(QgsPluginBaseTest):
    required_files = [GPKG_EKSPORT]

    def setUp(self):
        super().setUp()
        gpkg = GPKG_EKSPORT
        
        self.dialog.obszary_layer = self.loadLayer(gpkg, self.module_const.NAME_LAYER_OBSZARY, self.module_const.NAME_LAYER_OBSZARY)
        self.dialog.linie_layer = self.loadLayer(gpkg, self.module_const.NAME_LAYER_LINIE, self.module_const.NAME_LAYER_LINIE)
        self.dialog.drogi_layer = self.loadLayer(gpkg, self.module_const.NAME_LAYER_DROGI, self.module_const.NAME_LAYER_DROGI)
        self.dialog.nadlesnictwo = self.loadLayer(gpkg, self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'], self.module_const.INPUT_LAYERS['nadlesnictwo']['layer_name'])
    
        self.project.addMapLayers([
            self.dialog.obszary_layer, 
            self.dialog.linie_layer, 
            self.dialog.drogi_layer, 
            self.dialog.nadlesnictwo
        ])

        self.output_img = os.path.join(self.data_dir, FILENAME_WYDRUK_PDF)

    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.Utils.openFile')
    @patch('qgis.PyQt.QtWidgets.QFileDialog.getSaveFileName')
    @patch(f'{PLUGIN_NAME}.photovoltaics_LP_dialog.Utils.pushMessage')
    def testGenerujWydrukKompletny(self, mock_push, mock_save, mock_open):
        print("\n" + "=" * 50)
        print(f"\n [TEST] Weryfikacja zawartości wydruku")

        mock_save.return_value = (self.output_img, "pdf")

        # Uruchomienie generatora
        self.dialog.generujWydruk()

        # Pobranie layoutu
        layout_manager = self.project.layoutManager()
        layouts = layout_manager.printLayouts()
        self.assertGreater(len(layouts), 0, "Nie utworzono layoutu!")
        
        layout = layouts[0]
        items = layout.items()

        # Weryfikacja mapy
        map_item = self._verifyMap(items)
        
        # Weryfikacja legendy
        self._verifyLegend(items, map_item)

        # Weryfikacja tytułu
        self._verifyTitle(items)
        
        # Weryfikacja obrazów
        self._verifyPictures(items)

        print(f" [WYNIK] Wydruk kompletny: Obszary, Linie i Drogi są na mapie i w legendzie, tytuły są poprawne, obrazy są na miejscach. \n")
        print("=" * 50)

    def _verifyMap(self, items):
        """Sprawdza czy mapa zawiera wymagane warstwy."""
        maps = [i for i in items if isinstance(i, QgsLayoutItemMap)]
        self.assertEqual(len(maps), 1, "Brak elementu mapy w layoucie")
        
        map_item = maps[0]
        map_layer_names = [l.name() for l in map_item.layers()]
        
        expected = [
            self.module_const.NAME_LAYER_OBSZARY,
            self.module_const.NAME_LAYER_LINIE,
            self.module_const.NAME_LAYER_DROGI
        ]
        
        for name in expected:
            self.assertIn(name, map_layer_names, f"Warstwa {name} nie została dodana do mapy")
        
        return map_item

    def _verifyLegend(self, items, map_item):
        """Sprawdza poprawność legendy i jej powiązanie z mapą."""
        legends = [i for i in items if isinstance(i, QgsLayoutItemLegend)]
        self.assertEqual(len(legends), 1, "Brak elementu legendy")
        
        legend = legends[0]
        self.assertEqual(legend.linkedMap(), map_item, "Legenda nie jest powiązana z mapą")
        
        nodes = legend.model().rootGroup().findLayers()
        legend_layer_names = [n.name() for n in nodes if n is not None]
        
        expected = [
            self.module_const.NAME_LAYER_OBSZARY,
            self.module_const.NAME_LAYER_LINIE,
            self.module_const.NAME_LAYER_DROGI
        ]
        
        for name in expected:
            self.assertIn(name, legend_layer_names, f"Warstwa {name} nie widnieje w legendzie")

    def _verifyTitle(self, items):
        """Sprawdza czy tytuł wydruku jest poprawnie sformatowany."""
        labels = [i for i in items if isinstance(i, QgsLayoutItemLabel)]
        
        attr_name = self.module_const.LAYOUT_CONFIG['TITLE']['ATTR_NAME']
        nazwa_nadl = self.module_utils.Utils.pobierzNazweZWarstwy(self.dialog.nadlesnictwo, attr_name, self.iface_mock)
        
        oczekiwany_tytul = self.module_const.LAYOUT_CONFIG['TITLE']['TEXT_TEMPLATE'].format(nazwa_nadl)
        
        has_correct_title = any(l.text() == oczekiwany_tytul for l in labels)
        self.assertTrue(has_correct_title, f"Brak poprawnego tytułu. Oczekiwano: '{oczekiwany_tytul}'")

    def _verifyPictures(self, items):
        """Sprawdza czy w wydruku znajdują się wymagane elementy graficzne."""
        pictures = [i for i in items if isinstance(i, QgsLayoutItemPicture)]
        self.assertEqual(len(pictures), 3, "Brak logotypów lub strzałki północy (powinny być 3 obrazy)")

    def tearDown(self):
        if os.path.exists(self.output_img):
            try: os.remove(self.output_img)
            except: pass
        self.project.layoutManager().clear()
        super().tearDown()