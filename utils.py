import sys
import os
import processing

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    Qgis,
    QgsMessageLog,
    QgsLineSymbol,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsWkbTypes
)
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
from . import PLUGIN_NAME
from .constants import LAYER_STYLES


def onlyNewest(dataFilelist):
    """filtruje listę tylko do najnowszych plików według arkuszy"""
    aktualneDict = {}
    for dataFile in dataFilelist:
        godlo = dataFile.godlo
        if godlo in aktualneDict:
            old = aktualneDict[godlo]
            if dataFile.aktualnosc > old.aktualnosc:
                aktualneDict[godlo] = dataFile
        else:
            aktualneDict[godlo] = dataFile
    return list(aktualneDict.values())


def openFile(filename):
    """otwiera folder/plik niezależnie od systemu operacyjnego"""
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        import subprocess
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def pointTo2180(point, sourceCrs, project):
    """zamiana układu na 1992"""
    crsDest = QgsCoordinateReferenceSystem(2180)  # PL 1992
    xform = QgsCoordinateTransform(sourceCrs, crsDest, project)
    point1992 = xform.transform(point)

    return point1992

def layerTo2180(layer):
    """zamiana układu na 1992"""
    proc = processing.run("native:reprojectlayer",
                   {'INPUT': layer,
                    'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
    return proc['OUTPUT']

def createPointsFromPointLayer(layer):
    points = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if geom.isMultipart():
            mp = geom.asMultiPoint()
            points.extend(mp)
        else:
            points.append(geom.asPoint())
    return points

def createPointsFromLineLayer(layer, density):
    points = []
    for feat in layer.getFeatures():
        geom = feat.geometry()
        for point in geom.densifyByDistance(density).vertices():
            if point not in points:
                points.append(point)
    return points

def createPointsFromPolygon(layer, density=1000):
    punktyList = []

    for feat in layer.getFeatures():
        geom = feat.geometry()
        bbox = geom.boundingBox()
        if bbox.width() <= density or bbox.height() <= density:
            punktyList.append(bbox.center())
        else:
            params = {
                'TYPE':0,
                'EXTENT':bbox,
                'HSPACING':density,
                'VSPACING':density,
                'HOVERLAY':0,
                'VOVERLAY':0,
                'CRS':QgsCoordinateReferenceSystem('EPSG:2180'),
                'OUTPUT':'memory:TEMPORARY_OUTPUT'
            }
            proc = processing.run("qgis:creategrid", params)
            punkty = proc['OUTPUT']


            for pointFeat in punkty.getFeatures():
                point = pointFeat.geometry().asPoint()
                if geom.contains(point):
                    punktyList.append(point)


            # dodanie werteksów poligonu
            # uproszczenie geometrii
            geom2 = geom.simplify(800)
            for point in geom2.vertices():
                punktyList.append(point)


    return punktyList

def pushMessageBoxCritical(self, title: str, message: str):
    msg_box = QMessageBox(
        QMessageBox.Critical,
        title,
        message,
        QMessageBox.StandardButton.Ok
    )
    if hasattr(self, 'plugin_icon'):
        msg_box.setWindowIcon(QIcon(self.plugin_icon))
    msg_box.exec()

def pushMessageBox(self, message):
    msg_box = QMessageBox(
        QMessageBox.Information,
        'Informacja',
        message,
        QMessageBox.StandardButton.Ok
    )
    if hasattr(self, 'plugin_icon'):
        msg_box.setWindowIcon(QIcon(self.plugin_icon))
    msg_box.exec()

def pushMessage(iface, message: str) -> None:
    iface.messageBar().pushMessage(
        'Informacja',
        message,
        level=Qgis.Info,
        duration=10
    )

def pushWarning(iface, message: str) -> None:
    iface.messageBar().pushMessage(
        'Ostrzeżenie',
        message,
        level=Qgis.Warning,
        duration=10
    )


@staticmethod
def pushLogInfo(message: str) -> None:
    QgsMessageLog.logMessage(
        message,
        tag=PLUGIN_NAME,
        level=Qgis.Info
    )

@staticmethod
def pushLogWarning(message: str) -> None:
    QgsMessageLog.logMessage(
        message,
        tag=PLUGIN_NAME,
        level=Qgis.Warning
    )

@staticmethod
def pushLogCritical(message: str) -> None:
    QgsMessageLog.logMessage(
        message,
        tag=PLUGIN_NAME,
        level=Qgis.Critical
    )


def applyLayerStyle(layer, style_name):
    """
    Aplikuje styl do warstwy pobierając konfigurację 1:1 z constants.LAYER_STYLES.
    """
    
    if style_name not in LAYER_STYLES:
        return

    props = LAYER_STYLES[style_name]
    
    geom_type = layer.geometryType()
    
    if geom_type == QgsWkbTypes.PolygonGeometry:
        symbol = QgsFillSymbol.createSimple(props)
    else:
        symbol = QgsLineSymbol.createSimple(props)
    if symbol:
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.triggerRepaint()
