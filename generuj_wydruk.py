from qgis.core import *
from PyQt5.QtGui import QFont


class GenerujWydruk():
    """Klasa generująca obraz.
    """

    def generuj_wydruk(self, warstwy, kolor_tla, nazwa_pliku, nazwa_nadlesnictwa):
        """creates complex map layout consisting of map views, title, legend and scalebar and exports it to raster image.

        Args:
            warstwa (list): lista warstw dołączonych do wydruku mapy (QgsVectorLayer).
            kolor_tla (QColor): kolor tła mapy
            nazwa_pliku (str): ścieżka eksportu
            nazwa_nadlesnictwa (str): nazwa nadleśnictwa
        """
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        map = QgsLayoutItemMap(layout)
        map.setRect(20, 20, 20, 20)
        ms = QgsMapSettings()
        ms.setLayers(warstwy)  
        rect = QgsRectangle(ms.fullExtent())
        rect.scale(1.0)
        ms.setExtent(rect)
        map.setExtent(rect)
        map.setBackgroundColor(kolor_tla)
        layout.addLayoutItem(map)
        map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
        map.attemptResize(QgsLayoutSize(
            180, 180, QgsUnitTypes.LayoutMillimeters))
        title = QgsLayoutItemLabel(layout)
        title.setText("Obszary wyznaczone na potrzeby farm fotowoltaicznych - Nadleśnictwo {}".format(nazwa_nadlesnictwa))
        title.setFont(QFont('Arial', 13))
        title.adjustSizeToText()
        layout.addLayoutItem(title)
        title.attemptMove(QgsLayoutPoint(
            50, 5, QgsUnitTypes.LayoutMillimeters))
        title.setFrameEnabled(False)
        legend = QgsLayoutItemLegend(layout)
        legend.setLinkedMap(map)
        layerTree = QgsLayerTree()

        for warstwa in warstwy:
            layerTree.addLayer(warstwa)

        legend.model().setRootGroup(layerTree)
        layout.addLayoutItem(legend)
        legend.attemptMove(QgsLayoutPoint(
            215, 15, QgsUnitTypes.LayoutMillimeters))
        scaleBar = QgsLayoutItemScaleBar(layout)
        scaleBar.setStyle('Single Box')
        scaleBar.setFont(QFont("Arial", 10))
        scaleBar.applyDefaultSize(QgsUnitTypes.DistanceMeters)
        scaleBar.setMapUnitsPerScaleBarUnit(1000.0)
        scaleBar.setSegmentSizeMode(QgsScaleBarSettings.SegmentSizeFitWidth)
        scaleBar.setMaximumBarWidth(70)
        scaleBar.setNumberOfSegments(5)
        scaleBar.setUnitsPerSegment(1*1000.0)
        scaleBar.setUnitLabel("km")
        scaleBar.setLinkedMap(map)
        layout.addLayoutItem(scaleBar)
        scaleBar.attemptMove(QgsLayoutPoint(
            215, 190, QgsUnitTypes.LayoutMillimeters))
        exporter = QgsLayoutExporter(layout)
        exporter.exportToImage(
            nazwa_pliku, QgsLayoutExporter.ImageExportSettings())
