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
    QgsWkbTypes,
    QgsProject
)
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QIcon
from . import PLUGIN_NAME
from .constants import LAYER_STYLES, NAME_LAYER_OBSZARY, NAME_LAYER_LINIE, NAME_LAYER_DROGI



class FileUtils:

    @staticmethod
    def openFile(filename):
        """otwiera folder/plik niezależnie od systemu operacyjnego"""
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

class MessageUtils:

    @staticmethod
    def pushMessageBoxCritical(parent, title: str, message: str):
        msg_box = QMessageBox(
            QMessageBox.Icon.Critical,
            title,
            message,
            QMessageBox.StandardButton.Ok,
            parent
        )
        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))
        msg_box.exec()

    @staticmethod
    def pushMessageBox(parent, message):
        msg_box = QMessageBox(
            QMessageBox.Icon.Information,
            'Informacja',
            message,
            QMessageBox.StandardButton.Ok,
            parent
        )
        if hasattr(parent, 'plugin_icon'):
            msg_box.setWindowIcon(QIcon(parent.plugin_icon))
        msg_box.exec()

    @staticmethod
    def pushMessage(iface, message: str) -> None:
        iface.messageBar().pushMessage(
            'Informacja',
            message,
            level=Qgis.Info,
            duration=10
        )

    @staticmethod
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


class LayerUtils:

    @staticmethod
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

    @staticmethod
    def getNameFromLayer(warstwa, attr_name, iface):
        """Pobiera tekst z konkretnego atrybutu pierwszego obiektu warstwy."""
        if warstwa:
            feat = next(warstwa.getFeatures(), None)
            if feat:
                try: 
                    return str(feat[attr_name])
                except KeyError: 
                    MessageUtils.pushWarning(iface, "Błąd: Brak pola " + attr_name)
            else:
                    MessageUtils.pushWarning(iface, "Błąd: Nie znaleziono obiektu w warstwie " + warstwa.name())
        return "Nieznany"

    @staticmethod
    def getLayerByName(name: str, project: QgsProject = None):
        """
        Bezpiecznie zwraca obiekt warstwy o podanej nazwie lub None, jeśli nie znaleziona.
        """
        proj = project or QgsProject.instance()
        layers = proj.mapLayersByName(name)
        return layers[0] if layers else None


    @staticmethod
    def getResultLayers(project: QgsProject = None):
        """
        Zwraca słownik z obiektami warstw wynikowych.
        """
        return {
            'obszary': LayerUtils.getLayerByName(NAME_LAYER_OBSZARY, project),
            'linie': LayerUtils.getLayerByName(NAME_LAYER_LINIE, project),
            'drogi': LayerUtils.getLayerByName(NAME_LAYER_DROGI, project)
        }
