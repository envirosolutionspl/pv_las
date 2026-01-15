import os
from qgis.core import (
    QgsProject,
    QgsPrintLayout,
    QgsLayoutItemLegend,
    QgsLayerTree,
    QgsLayoutItemScaleBar,
    QgsScaleBarSettings,
    QgsLayoutExporter,
    QgsRenderContext,
    QgsMapLayerType,
    QgsCoordinateReferenceSystem,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemLabel,
    QgsTextFormat,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
    QgsRectangle,
    QgsLayoutItemPage
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QFileDialog

from ..constants import (
    LAYOUT_CONFIG, NAME_LAYER_OBSZARY, NAME_LAYER_LINIE, 
    NAME_LAYER_DROGI, FILE_FILTERS, CRS_EPSG
)
from ..utils import getResultLayers, pushWarning, pobierzNazweZWarstwy

class WydrukGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.project = parent.project
        self.iface = parent.iface
        self.lc = LAYOUT_CONFIG
        
        # Pobieranie nadleśnictwa z parenta
        self.nadlesnictwo = getattr(parent, 'nadlesnictwo', None)
        self.plugin_dir = os.path.dirname(os.path.dirname(__file__))

        # Pobieranie warstw
        self.warstwy = self._pobierzWarstwy()
        
        # Zmienna do przechowywania drzewa warstw
        self.layer_tree = None 

    def _pobierzWarstwy(self):
        """Pobiera warstwy wynikowe oraz widoczne podkłady rastrowe."""
        wszystkie = []
        
        # Warstwy wektorowe (wyniki)
        results = getResultLayers(self.project)
        wszystkie.extend([l for l in results.values() if l])
        
        # Warstwy rastrowe 
        for layer in self.project.mapLayers().values():
            if layer.type() == QgsMapLayerType.RasterLayer:
                node = self.project.layerTreeRoot().findLayer(layer.id())
                if node and node.isVisible():
                    wszystkie.append(layer)
        
        return wszystkie

    def generuj(self):
        """Główna funkcja wydruku"""
        nazwa_pliku, _ = QFileDialog.getSaveFileName(None, "Zapisz jako ...", "", filter=FILE_FILTERS['IMAGES'])
        
        if not nazwa_pliku:
            return None

        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()
        
        # Zapobieganie konfliktom nazw - usuwamy stary layout o tej samej nazwie
        layout_name = "Wydruk Farmy PV"
        existing = self.project.layoutManager().layoutByName(layout_name)
        if existing:
            self.project.layoutManager().removeLayout(existing)
            
        layout.setName(layout_name)
        self.project.layoutManager().addLayout(layout)
        
        # Ustawienie rozmiaru strony
        page = layout.pageCollection().pages()[0]
        page.setPageSize(QgsLayoutSize(
            self.lc['PAGE']['SIZE_W'], 
            self.lc['PAGE']['SIZE_H'], 
            QgsUnitTypes.LayoutMillimeters
        ))

        # Przygotowanie zasięgu mapy
        extent = self._obliczZasiegMapy(self.lc['MAP']['EXTENT_SCALE'])

        # Nazwa nadleśnictwa
        nazwa_nadl = pobierzNazweZWarstwy(self.nadlesnictwo, self.lc['TITLE']['ATTR_NAME'], self.iface)
        tytul_pelny = self.lc['TITLE']['TEXT_TEMPLATE'].format(nazwa_nadl)
        
        # Przygotowanie warstw wynikowych
        warstwy_wynikowe = [l for l in self.warstwy if l.name() in [NAME_LAYER_OBSZARY, NAME_LAYER_LINIE, NAME_LAYER_DROGI]]

        # Wywołanie rysowania
        map_item = self._dodajMape(layout, self.lc['MAP'], self.warstwy, extent)
        
        self._dodajTytul(layout, self.lc['TITLE'], tytul_pelny)
        self._dodajStopke(layout, self.lc['FOOTER'])

        for key in ['LOGO_LP', 'LOGO_ENV', 'ARROW']:
            path = os.path.join(self.plugin_dir, self.lc[key]['PATH'])
            self._dodajObraz(layout, self.lc[key], path)
            
        self._dodajLegende(layout, map_item, self.lc['LEGEND'], warstwy_wynikowe)
        self._dodajSkaleLiczbowa(layout, map_item, self.lc['NUMERIC_SCALE'])
        self._dodajSkale(layout, map_item, self.lc['SCALEBAR'])

        # Odświeżenie
        layout.refresh()
        map_item.refresh()

        # Eksport
        exporter = QgsLayoutExporter(layout)
        if nazwa_pliku.lower().endswith('.pdf'):
            pdf_settings = QgsLayoutExporter.PdfExportSettings()

            
            exporter.exportToPdf(nazwa_pliku, pdf_settings)
        else:
            # Poprawka dla błędu dostępu przy aktualizacji sterownika JPEG: usuń plik jeśli istnieje
            if os.path.exists(nazwa_pliku):
                try:
                    os.remove(nazwa_pliku)
                except PermissionError:
                    pushWarning(self.iface, f"Błąd: Plik {os.path.basename(nazwa_pliku)} jest używany przez inny program. Zamknij go i spróbuj ponownie.")
                    return None
                except OSError as e:
                    pushWarning(self.iface, f"Nie udało się usunąć istniejącego pliku: {e}")
                    return None

            exporter.exportToImage(nazwa_pliku, QgsLayoutExporter.ImageExportSettings())
            
        return nazwa_pliku

    def _dodajMape(self, layout, config, layers, extent):
        """
        Tworzy i pozycjonuje mapę.
        Args:
            layout (QgsLayout): Layout do którego dodawana jest mapa.
            config (dict): Konfiguracja mapy.
            layers (list): Lista warstw do pokazania na mapie.
            extent (QgsRectangle): Obszar mapy.
        """
        map_item = QgsLayoutItemMap(layout)
        layout.addLayoutItem(map_item)

        map_item.setLayers(layers)
        map_item.setKeepLayerSet(True)
        map_item.setCrs(QgsCoordinateReferenceSystem(f"EPSG:{CRS_EPSG}"))
        
        map_item.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))
        map_item.attemptResize(QgsLayoutSize(config['SIZE_W'], config['SIZE_H'], QgsUnitTypes.LayoutMillimeters))
        
        map_item.setExtent(extent)
        map_item.attemptResize(QgsLayoutSize(config['SIZE_W'], config['SIZE_H'], QgsUnitTypes.LayoutMillimeters))
        
        map_item.setFrameEnabled(True)
        map_item.setBackgroundEnabled(True)
        map_item.setBackgroundColor(QColor(255, 255, 255))  
        
        return map_item

    def _dodajObraz(self, layout, config, path):
        """Tworzy i pozycjonuje obraz.
        Args:
            layout (QgsLayout): Layout do którego dodawany jest obraz.
            config (dict): Konfiguracja obrazu.
            path (str): Ścieżka do obrazu.
        """
        pic = QgsLayoutItemPicture(layout)
        pic.setPicturePath(path)
        pic.setResizeMode(QgsLayoutItemPicture.Zoom)
        layout.addLayoutItem(pic)

        width = config['ORIG_W'] * config['SCALE']
        height = config['ORIG_H'] * config['SCALE']

        pic.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))
        pic.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutPixels))

    def _dodajStopke(self, layout, config):
        """Tworzy i pozycjonuje stopkę.
        Args:
            layout (QgsLayout): Layout do którego dodawana jest stopka.
            config (dict): Konfiguracja stopki.
        """
        footer = QgsLayoutItemLabel(layout)
        footer.setText(config['TEXT'])
        
        txt_format = QgsTextFormat()
        txt_format.setFont(QFont(config['FONT_TYPE'], config['FONT_SIZE']))
        footer.setTextFormat(txt_format)
        
        layout.addLayoutItem(footer)
        
        footer.attemptMove(QgsLayoutPoint(
            config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _dodajTytul(self, layout, config, tekst):
        """
        Tworzy i pozycjonuje tytuł.
        Automatyczne dopasowanie rozmiaru ramki do tekstu.
        Args:
            layout (QgsLayout): Layout do którego dodawany jest tytuł.
            config (dict): Konfiguracja tytułu. 
            tekst (str): Tekst tytułu.
        """
        title = QgsLayoutItemLabel(layout)
        title.setText(tekst)
        
        txt_format = QgsTextFormat()
        txt_format.setFont(QFont(config['FONT_TYPE'], config['FONT_SIZE']))
        title.setTextFormat(txt_format)
        
        title.adjustSizeToText()
        title.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))
        layout.addLayoutItem(title)
    
    def _dodajLegende(self, layout, map_item, config, layers_to_show):
        """
        Tworzy i pozycjonuje legende.
        Args:
            layout (QgsLayout): Layout do którego dodawana jest legenda.
            map_item (QgsLayoutItemMap): Mapa do której jest powiazana legenda.
            config (dict): Konfiguracja legendy.
            layers_to_show (list): Lista warstw do pokazania w legendzie.
        """
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map_item)
        legend.setAutoUpdateModel(False)
        
        # Budowanie drzewa warstw
        root = legend.model().rootGroup()
        root.clear()
        for lyr in layers_to_show:
            if lyr:
                root.addLayer(lyr)

        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _dodajSkale(self, layout, map_item, config):
        """
        Tworzy i pozycjonuje miarkę.
        Args:
            layout (QgsLayout): Layout do którego dodawana jest miarka.
            map_item (QgsLayoutItemMap): Mapa do której jest powiazana miarka.
            config (dict): Konfiguracja miarki.
        """
        scaleBar = QgsLayoutItemScaleBar(layout)
        scaleBar.setLinkedMap(map_item)
        layout.addLayoutItem(scaleBar)
        
        scaleBar.setUnits(QgsUnitTypes.DistanceKilometers)
        scaleBar.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeFixed) 
        scaleBar.setUnitsPerSegment(config['UNITS_PER_SEGMENT']) 
        scaleBar.setNumberOfSegments(config['SEGMENTS']) 
        scaleBar.setNumberOfSegmentsLeft(0)
        
        scaleBar.setStyle('Single Box')
        scaleBar.setUnitLabel(config['UNIT_LABEL']) 
        
        txt_format = QgsTextFormat()
        txt_format.setFont(QFont(config['FONT_TYPE'], config['FONT_SIZE']))
        scaleBar.setTextFormat(txt_format)
        
        scaleBar.update()
        scaleBar.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _dodajSkaleLiczbowa(self, layout, map_item, config):
        """
        Dodaje skalę liczbową (1:X) do layoutu.
        """
        label = QgsLayoutItemLabel(layout)
        # Pobieramy skalę z mapy i zaokrąglamy
        scale_val = int(round(map_item.scale()))
        label.setText(f"{config['PREFIX']}{scale_val}")
        
        txt_format = QgsTextFormat()
        txt_format.setFont(QFont(config['FONT_TYPE'], config['FONT_SIZE']))
        label.setTextFormat(txt_format)
        
        label.adjustSizeToText()
        layout.addLayoutItem(label)
        label.attemptMove(QgsLayoutPoint(config['POS_X'], config['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _obliczZasiegMapy(self, config_scale):
        """Oblicza zasięg na podstawie nadleśnictwa lub wszystkich warstw."""
        extent = QgsRectangle()
        if self.nadlesnictwo:
            feat = next(self.nadlesnictwo.getFeatures(), None)
            if feat:
                extent = feat.geometry().boundingBox()
        
        if extent.isEmpty() and self.warstwy:
            for lyr in self.warstwy:
                extent.combineExtentWith(lyr.extent())
        
        if extent.isEmpty():
            extent = self.iface.mapCanvas().extent()

        extent.scale(config_scale)
        return extent