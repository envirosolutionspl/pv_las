import os
import sys
import time
import gc
import unittest
import importlib
from unittest.mock import MagicMock
import urllib.request
import urllib.error
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsTask
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import QEventLoop, QTimer

from .constants import TEST_DIR, DATA_DIR, TEST_DATA_BASE_URL

PLUGIN_DIR = os.path.dirname(TEST_DIR)
PARENT_DIR = os.path.dirname(PLUGIN_DIR)
PLUGIN_NAME = os.path.basename(PLUGIN_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

def _initQgis():
    global _qgs_app
    if QgsApplication.instance() is None:
        _qgs_app = QgsApplication([], False)
        _qgs_app.initQgis()
        
        # Inicjalizacja processing
        prefix = QgsApplication.prefixPath()
        proc_path = os.path.join(prefix, "python", "plugins")
        if proc_path not in sys.path:
            sys.path.append(proc_path)
            
        import processing
        from processing.core.Processing import Processing
        Processing.initialize()
    else:
        _qgs_app = QgsApplication.instance()
    return _qgs_app

# Inicjalizacja QGIS
_qgs_app = _initQgis()

class QgsPluginBaseTest(unittest.TestCase):
    qgs_app = _qgs_app
    project = None
    iface_mock = None
    dialog = None
    
    # Lista plików wymaganych przez daną klasę testową (nadpisywana w podklasach)
    required_files = [] 
    
    module_dialog = None
    module_const = None
    module_utils = None

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
            
            if not os.path.exists(path):
                print(f" [INFO] Pobieranie: {filename}...")
                try:
                    urllib.request.urlretrieve(url, path)
                except urllib.error.URLError as e:
                    print(f" [BŁĄD] Sieciowy podczas pobierania {filename}: {e.reason}")
                except OSError as e:
                    print(f" [BŁĄD] Systemowy podczas zapisu pliku {filename}: {e.strerror}")

    @classmethod
    def cleanupTestData(cls):
        """Zostawiamy pliki na dysku (Cache)."""
        pass

    @classmethod
    def setUpClass(cls):
        """Inicjalizacja raz na całą klasę testową."""
        cls.downloadTestData()
        cls.project = QgsProject.instance()
        
        # Importy modułów
        if cls.module_dialog is None:
            cls.module_dialog = importlib.import_module(f"{PLUGIN_NAME}.photovoltaics_LP_dialog")
            cls.module_const = importlib.import_module(f"{PLUGIN_NAME}.constants")
            cls.module_utils = importlib.import_module(f"{PLUGIN_NAME}.utils")

        # Wspólny mock dla iface
        cls.iface_mock = MagicMock()
        cls.iface_mock.mapCanvas.return_value = MagicMock(spec=QgsMapCanvas)
        cls.module_dialog.iface = cls.iface_mock

        # Jedna instancja dialogu na klasę testową
        cls.dialog = cls.module_dialog.PhotovoltaicsLPDialog(None)

    @classmethod
    def tearDownClass(cls):
        """Czyszczenie po wszystkich testach w klasie."""
        # Usuwamy warstwy z projektu QGIS
        if cls.project:
            cls.project.clear()
        
        # Czyścimy obiekt dialogu (zwalniamy referencje do warstw)
        work_dir = None
        if cls.dialog:
            work_dir = getattr(cls.dialog, 'work_dir', None)
            cls.dialog = None
        
        # Wymuszamy zwolnienie pamięci i uchwytów do plików
        gc.collect()
        QgsApplication.processEvents()
        time.sleep(0.1)

        if work_dir:
            try:
                work_dir.cleanup()
            except (OSError, PermissionError):
                pass

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
        gc.collect()
    
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