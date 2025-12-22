import os
from qgis.core import (
    QgsPrintLayout, QgsLayoutItemMap, QgsRectangle, QgsLayoutPoint, 
    QgsLayoutSize, QgsUnitTypes, QgsLayoutItemPicture, QgsLayoutItemLabel, 
    QgsLayoutItemLegend, QgsLayerTree, QgsLayoutItemScaleBar, 
    QgsScaleBarSettings, QgsLayoutExporter, QgsMapLayerType
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QFileDialog

from ..constants import (
    LAYOUT_CONFIG, NAME_LAYER_OBSZARY, NAME_LAYER_LINIE, 
    NAME_LAYER_DROGI
)

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
        self.warstwy = self._pobierz_warstwy()
        
        # Zmienna do przechowywania drzewa warstw
        self.layer_tree = None 

    def _pobierz_warstwy(self):
        """Pobiera warstwy wynikowe oraz widoczne podkłady rastrowe."""
        wszystkie = []
        
        # Warstwy wektorowe (wyniki)
        for nazwa in [NAME_LAYER_OBSZARY, NAME_LAYER_DROGI, NAME_LAYER_LINIE]:
            layers = self.project.mapLayersByName(nazwa)
            if layers:
                wszystkie.append(layers[0])
        
        # Warstwy rastrowe 
        for layer in self.project.mapLayers().values():
            if layer.type() == QgsMapLayerType.RasterLayer:
                node = self.project.layerTreeRoot().findLayer(layer.id())
                if node and node.isVisible():
                    wszystkie.append(layer)
        
        return wszystkie

    def generuj(self):
        """Główna funkcja wydruku"""
        typy_obrazu = "jpg (*.jpg);;bitmap (*.bmp);;tiff (*.tiff);; pdf (*.pdf)"
        nazwa_pliku, _ = QFileDialog.getSaveFileName(None, "Zapisz jako ...", "", filter=typy_obrazu)
        
        if not nazwa_pliku:
            return None

        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()

        # Kolejność tworzenia modułów
        map_item = self._dodaj_mape(layout)
        self._dodaj_obrazy(layout)
        self._dodaj_tytul(layout)
        self._dodaj_stopke(layout)
        self._dodaj_legende(layout, map_item)
        self._dodaj_skale(layout, map_item)

        # Eksport
        exporter = QgsLayoutExporter(layout)
        if nazwa_pliku.lower().endswith('.pdf'):
            exporter.exportToPdf(nazwa_pliku, QgsLayoutExporter.PdfExportSettings())
        else:
            exporter.exportToImage(nazwa_pliku, QgsLayoutExporter.ImageExportSettings())
            
        return nazwa_pliku

    def _dodaj_mape(self, layout):
        """Tworzy i pozycjonuje mapę."""
        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(*self.lc['MAP']['RECT'])
        
        extent = QgsRectangle()
        if self.nadlesnictwo:
            feat = next(self.nadlesnictwo.getFeatures(), None)
            if feat:
                extent = feat.geometry().boundingBox()
        
        if extent.isEmpty() and self.warstwy:
            for lyr in self.warstwy:
                extent.combineExtentWith(lyr.extent())

        extent.scale(self.lc['MAP']['EXTENT_SCALE'])
        map_item.setExtent(extent)
        map_item.setLayers(self.warstwy)
        map_item.setBackgroundColor(QColor(255, 255, 255))
        
        layout.addLayoutItem(map_item)
        map_item.attemptMove(QgsLayoutPoint(
            self.lc['MAP']['POS_X'], self.lc['MAP']['POS_Y'], QgsUnitTypes.LayoutMillimeters))
        map_item.attemptResize(QgsLayoutSize(
            self.lc['MAP']['SIZE_W'], self.lc['MAP']['SIZE_H'], QgsUnitTypes.LayoutMillimeters))
        return map_item

    def _dodaj_obrazy(self, layout):
        """Tworzy i pozycjonuje obrazy."""
        for key in ['LOGO_LP', 'LOGO_ENV', 'ARROW']:
            cfg = self.lc[key]
            pic = QgsLayoutItemPicture(layout)
            pic.setResizeMode(QgsLayoutItemPicture.Zoom)
            pic.setMode(QgsLayoutItemPicture.FormatRaster)
            pic.setPicturePath(os.path.join(self.plugin_dir, cfg['PATH']))

            dim = [cfg['ORIG_W'] * cfg['SCALE'], cfg['ORIG_H'] * cfg['SCALE']]
            layout.addLayoutItem(pic)
            pic.attemptMove(QgsLayoutPoint(cfg['POS_X'], cfg['POS_Y'], QgsUnitTypes.LayoutMillimeters))
            pic.attemptResize(QgsLayoutSize(*dim, QgsUnitTypes.LayoutPixels))

    def _dodaj_stopke(self, layout):
        """Tworzy i pozycjonuje stopkę."""
        cfg = self.lc['FOOTER']
        
        footer = QgsLayoutItemLabel(layout)
        footer.setText(cfg['TEXT'])
        footer.setFont(QFont('Arial', cfg['FONT_SIZE']))
        
        layout.addLayoutItem(footer)
        
        footer.attemptMove(QgsLayoutPoint(
            cfg['POS_X'], cfg['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _dodaj_tytul(self, layout):
        """Tworzy i pozycjonuje tytuł."""
        cfg = self.lc['TITLE']
        nadl_name = ""
        if self.nadlesnictwo:
            feat = next(self.nadlesnictwo.getFeatures(), None)
            if feat:
                try: nadl_name = str(feat[self.lc['TITLE']['ATTR_NAME']])
                except: pass
        
        title = QgsLayoutItemLabel(layout)
        title.setText(cfg['TEXT_TEMPLATE'].format(nadl_name))
        title.setFont(QFont('Arial', cfg['FONT_SIZE']))
        title.adjustSizeToText()
        
        layout.addLayoutItem(title)
        
        # Ustawienie pozycji i rozmiaru
        title.attemptMove(QgsLayoutPoint(
            cfg['POS_X'], cfg['POS_Y'], QgsUnitTypes.LayoutMillimeters))
        title.attemptResize(QgsLayoutSize(
            cfg['SIZE_W'], cfg['SIZE_H'], QgsUnitTypes.LayoutMillimeters))

    def _dodaj_legende(self, layout, map_item):
        """Tworzy i pozycjonuje legende."""
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map_item)
        
        self.layer_tree = QgsLayerTree()
        wynikowe = [NAME_LAYER_OBSZARY, NAME_LAYER_LINIE, NAME_LAYER_DROGI]
        for lyr in self.warstwy:
            if lyr.name() in wynikowe:
                self.layer_tree.addLayer(lyr)

        legend.model().setRootGroup(self.layer_tree)
        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(
            self.lc['LEGEND']['POS_X'], self.lc['LEGEND']['POS_Y'], QgsUnitTypes.LayoutMillimeters))

    def _dodaj_skale(self, layout, map_item):
        """Tworzy i pozycjonuje miarkę."""
        lc = self.lc
        scaleBar = QgsLayoutItemScaleBar(layout)
        scaleBar.setStyle('Single Box')
        scaleBar.setFont(QFont("Arial", 9))
        scaleBar.applyDefaultSize(QgsUnitTypes.DistanceMeters)
        scaleBar.setMapUnitsPerScaleBarUnit(1000.0)
        scaleBar.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeFitWidth)
        scaleBar.setMaximumBarWidth(lc['SCALEBAR']['MAX_WIDTH'])
        scaleBar.setNumberOfSegments(lc['SCALEBAR']['SEGMENTS'])
        scaleBar.setUnitsPerSegment(1*1000.0)
        scaleBar.setUnitLabel(lc['SCALEBAR']['UNIT_LABEL'])
        scaleBar.setLinkedMap(map_item)
        
        layout.addLayoutItem(scaleBar)
        scaleBar.attemptMove(QgsLayoutPoint(
            lc['SCALEBAR']['POS_X'], lc['SCALEBAR']['POS_Y'], QgsUnitTypes.LayoutMillimeters))