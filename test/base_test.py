import os
import sys
import time
import gc
import unittest
import importlib
from unittest.mock import MagicMock
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QEventLoop, QUrl, QTimer
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsTask
from qgis.gui import QgsMapCanvas

from .constants import TEST_DIR, DATA_DIR, TEST_DATA_BASE_URL

PLUGIN_DIR = os.path.dirname(TEST_DIR)
PARENT_DIR = os.path.dirname(PLUGIN_DIR)
PLUGIN_NAME = os.path.basename(PLUGIN_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

def ensure_qgis():
    """Zapewnia instancję QgsApplication i zwraca ją."""
    instance = QgsApplication.instance()
    if instance is None:
        instance = QgsApplication([], False)
        instance.initQgis()
        
        # Inicjalizacja processing
        prefix = QgsApplication.prefixPath()
        proc_path = os.path.join(prefix, "python", "plugins")
        if proc_path not in sys.path:
            sys.path.append(proc_path)
            
        import processing
        from processing.core.Processing import Processing
        Processing.initialize()
    return instance

class QgsPluginBaseTest(unittest.TestCase):
    qgs_app = None
    network_manager = None
    project = None
    iface_mock = None
    dialog = None
    
    required_files = [] 
    module_dialog = None
    module_const = None
    module_utils = None

    @classmethod
    def setUpClass(cls):
        """Inicjalizacja raz na całą klasę testową."""
        cls.qgs_app = ensure_qgis()
        cls.network_manager = QNetworkAccessManager()
        cls.downloadTestData()
        cls.project = QgsProject.instance()
        
        if cls.module_dialog is None:
            cls.module_dialog = importlib.import_module(f"{PLUGIN_NAME}.photovoltaics_LP_dialog")
            cls.module_const = importlib.import_module(f"{PLUGIN_NAME}.constants")
            cls.module_utils = importlib.import_module(f"{PLUGIN_NAME}.utils")

        cls.iface_mock = MagicMock()
        cls.iface_mock.mapCanvas.return_value = MagicMock(spec=QgsMapCanvas)
        cls.module_dialog.iface = cls.iface_mock
        cls.dialog = cls.module_dialog.PhotovoltaicsLPDialog(None)

    @classmethod
    def downloadTestData(cls):
        """Pobiera pliki zdefiniowane w required_files."""
        if not cls.required_files:
            return

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        for filename in cls.required_files:
            url = f"{TEST_DATA_BASE_URL}{filename}"
            path = os.path.join(DATA_DIR, filename)
            
            if os.path.exists(path):
                continue

            print(f" [INFO] Pobieranie: {filename}...")
            
            request = QNetworkRequest(QUrl(url))
            reply = cls.network_manager.get(request)
            
            loop = QEventLoop()
            reply.finished.connect(loop.quit)
            loop.exec()

            if reply.error() == QNetworkReply.NoError:
                try:
                    data = reply.readAll()
                    with open(path, 'wb') as f:
                        f.write(data.data())
                except OSError as e:
                    print(f" [BŁĄD] Systemowy: {e.strerror}")
            else:
                print(f" [BŁĄD] Pobierania {filename}: {reply.errorString()}")
            
            reply.deleteLater()

    @classmethod
    def tearDownClass(cls):
        """Czyszczenie po testach."""
        if cls.project:
            cls.project.clear()
        
        cls.dialog = None
        cls.network_manager = None
        
        gc.collect()
        QgsApplication.processEvents()
        super(QgsPluginBaseTest, cls).tearDownClass()

    def setUp(self):
        """Przygotowanie przed każdym testem."""
        if self.project:
            self.project.clear()
        if self.dialog:
            self.dialog.resetuj()
        QgsApplication.processEvents()
        self.data_dir = os.path.join(TEST_DIR, 'data')

    def tearDown(self):
        """Czyszczenie po każdym teście."""
        if self.project:
            self.project.clear()
        
        if self.dialog:
            self.dialog.resetuj()

        gc.collect()
        QgsApplication.processEvents()
        time.sleep(0.2)
        if self.dialog and hasattr(self.dialog, 'work_dir'):
            if self.dialog.work_dir:
                try:
                    self.dialog.work_dir.cleanup()
                except (OSError, PermissionError) as e:
                    print(f" [DEBUG] Windows nadal blokuje pliki: {e}")
                finally:
                    self.dialog.work_dir = None

        QgsApplication.processEvents()
    
    def loadLayer(self, file_name, layer_name_in_gpkg=None, qgis_name="test_layer"):
        path = os.path.join(self.data_dir, file_name)
        if not os.path.exists(path):
            self.fail(f"Brak pliku testowego: {path}")

        uri = f"{path}|layername={layer_name_in_gpkg}" if layer_name_in_gpkg else path
        lyr = QgsVectorLayer(uri, qgis_name, "ogr")
        if not lyr.isValid():
            self.fail(f"Błąd wczytywania warstwy: {file_name}")
        return lyr


    def _startTimeoutTimer(self, loop, timeout):
        """Wydzielona logika timera bezpieczeństwa."""
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(timeout * 1000)
        return timer

    def waitForTask(self, task, timeout=60):
        """Czekanie na Task z obsługą bętli zdarzeń."""
        if not task:
            return

        loop = QEventLoop()
        task.taskCompleted.connect(loop.quit)
        task.taskTerminated.connect(loop.quit)
        
        timer = self._startTimeoutTimer(loop, timeout)

        if task.status() not in [QgsTask.Complete, QgsTask.Terminated]:
            loop.exec()
        
        try:
            final_status = task.status()
        except RuntimeError:
            # Jeżeli obiekt został już usunięty przez QGIS, przyjmujemy sukces
            final_status = QgsTask.Complete

        for _ in range(10): 
            QgsApplication.processEvents()
            time.sleep(0.05)

        if final_status != QgsTask.Complete:
            self.fail(f"Zadanie nie powiodło się lub zostało przerwane. Status: {final_status}")