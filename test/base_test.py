import os
import sys
import time
import gc
import unittest
import importlib
from unittest.mock import MagicMock
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsTask
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QEventLoop, QTimer

from .constants import TEST_DIR, DATA_DIR

# --- USTALANIE ŚCIEŻEK DO MOCKOWANIA ---
PLUGIN_DIR = os.path.dirname(TEST_DIR)
PARENT_DIR = os.path.dirname(PLUGIN_DIR)
PLUGIN_NAME = os.path.basename(PLUGIN_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

class QgsPluginBaseTest(unittest.TestCase):
    qgs_app = None
    module_dialog = None
    module_const = None

    @classmethod
    def setUpClass(cls):
        if QgsApplication.instance() is None:
            cls.qgs_app = QgsApplication([], False)
            cls.qgs_app.initQgis()
            prefix = QgsApplication.prefixPath()
            proc_path = os.path.join(prefix, "python", "plugins")
            if proc_path not in sys.path:
                sys.path.append(proc_path)
            
            import processing
            from processing.core.Processing import Processing
            Processing.initialize()
        else:
            cls.qgs_app = QgsApplication.instance()

        cls.module_dialog = importlib.import_module(f"{PLUGIN_NAME}.photovoltaics_LP_dialog")
        cls.module_const = importlib.import_module(f"{PLUGIN_NAME}.constants")
        cls.module_utils = importlib.import_module(f"{PLUGIN_NAME}.utils") 

    def setUp(self):
        QgsProject.instance().clear()
        
        self.iface_mock = MagicMock()
        self.iface_mock.mapCanvas.return_value = MagicMock(spec=QgsMapCanvas)
        self.module_dialog.iface = self.iface_mock
        
        self.dialog = self.module_dialog.PhotovoltaicsLPDialog(None)
        self.data_dir = os.path.join(TEST_DIR, 'data')

    def tearDown(self):
        """Czyszczenie po testach."""
        QgsProject.instance().removeAllMapLayers()
        
        if hasattr(self, 'dialog') and self.dialog:
            work_dir = getattr(self.dialog, 'work_dir', None)
            if work_dir:
                try:
                    work_dir.cleanup()
                except PermissionError:
                    # Jeżeli dalej jest blokowane, to ignorujemu
                    pass
            self.dialog = None

        gc.collect()
    
    def load_layer(self, file_name, layer_name_in_gpkg=None, qgis_name="test_layer"):
        path = os.path.join(self.data_dir, file_name)
        if not os.path.exists(path):
            self.fail(f"Brak pliku testowego: {path}")

        uri = f"{path}|layername={layer_name_in_gpkg}" if layer_name_in_gpkg else path
        lyr = QgsVectorLayer(uri, qgis_name, "ogr")
        if not lyr.isValid():
            self.fail(f"Błąd wczytywania warstwy: {file_name}")
        return lyr

    def wait_for_task(self, task, timeout=60):
        """Czekanie na Task z obsługą pętli zdarzeń."""
        if not task:
            self.fail("Próba czekania na Task, który jest None!")

        loop = QEventLoop()
        task.taskCompleted.connect(loop.quit)
        task.taskTerminated.connect(loop.quit)
        
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(timeout * 1000)

        if task.status() not in [QgsTask.Complete, QgsTask.Terminated]:
            loop.exec_()
        
        # Metoda finished() zadania jest wywoływana w pętli zdarzeń 
        # PO tym jak task zgłosi Completion. Trzeba poczekać. 
        for _ in range(30):
            QgsApplication.processEvents()
            time.sleep(0.1)