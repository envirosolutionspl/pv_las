# -*- coding: utf-8 -*-

import tempfile
import zipfile
import io
import os
import processing 
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl
from qgis.core import (
    QgsTask, 
    QgsBlockingNetworkRequest, 
    QgsVectorLayer, 
    QgsProject,
    Qgis
)
from ..constants import (
    BDOT10K_SHP_URL_TEMPLATE, BDOT_FILE_SUFFIX_DROGI, BDOT_FILE_SUFFIX_LINIE,
    LAYER_NAME_BDOT10K_DROGI, LAYER_NAME_BDOT10K_LINIE, CRS_EPSG
)
from ..utils import pushLogInfo, pushMessage, pushWarning, apply_layer_style

class PobierzBdotTask(QgsTask):

    def __init__(self, description, features, iface, temp_path, wczytajBdot10kBtn, analizaBtn, resetujBtn):
        super().__init__(description, QgsTask.CanCancel)
        self.project = QgsProject.instance()
        self.temp_dir_path = temp_path
        
        self.features = features 
        self.iface = iface
        self.wczytajBdot10kBtn = wczytajBdot10kBtn
        self.resetujBtn = resetujBtn
        self.analizaBtn = analizaBtn
        self.exception = None
        
        self.output_drogi_path = None
        self.output_linie_path = None
  
    def run(self):
        """Działa w tle"""
        pushLogInfo(f'Start RUN. Temp: {self.temp_dir_path}')
        try:
            import processing
            
            drogi_files = []
            linie_files = []

            for i, feature in enumerate(self.features):
                if self.isCanceled(): return False
                
                url = BDOT10K_SHP_URL_TEMPLATE.format(feature[1], feature[1]+feature[2])
                
                request = QgsBlockingNetworkRequest()
                request.get(QNetworkRequest(QUrl(url)))
                reply = request.reply()
                
                if reply.error() != QNetworkReply.NoError:
                    pushLogInfo(f"Błąd sieci: {reply.errorString()}")
                    continue
                    
                content = reply.content()
                if not content: continue

                try:
                    z = zipfile.ZipFile(io.BytesIO(content))
                    extract_path = os.path.join(self.temp_dir_path, str(i))
                    z.extractall(extract_path)
                
                    for root, dirs, files in os.walk(extract_path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            if file.endswith(BDOT_FILE_SUFFIX_DROGI):
                                drogi_files.append(full_path)
                            elif file.endswith(BDOT_FILE_SUFFIX_LINIE):
                                linie_files.append(full_path)
                except Exception as e:
                    pushLogInfo(f"Błąd Zip: {e}")

            if self.isCanceled(): return False

            if drogi_files:
                out_path = os.path.join(self.temp_dir_path, 'merged_drogi.gpkg')
                params = {'LAYERS': drogi_files, 'CRS': CRS_EPSG, 'OUTPUT': out_path}
                processing.run("native:mergevectorlayers", params)
                if os.path.exists(out_path):
                    self.output_drogi_path = out_path

            if linie_files:
                out_path = os.path.join(self.temp_dir_path, 'merged_linie.gpkg')
                params = {'LAYERS': linie_files, 'CRS': CRS_EPSG, 'OUTPUT': out_path}
                processing.run("native:mergevectorlayers", params)
                if os.path.exists(out_path):
                    self.output_linie_path = out_path
            
            pushLogInfo("Koniec RUN - sukces")
            return True

        except Exception as e:
            self.exception = e
            pushLogInfo(f"KRYTYCZNY BŁĄD w RUN: {e}")
            return False
    
    def finished(self, result):
        """Działa w głównym wątku"""
        pushLogInfo(f"FINISHED START. Wynik: {result}")
        
        try:
            if result:
                if self.output_drogi_path and os.path.exists(self.output_drogi_path):
                    vlayer = QgsVectorLayer(self.output_drogi_path, LAYER_NAME_BDOT10K_DROGI, "ogr")
                    if vlayer.isValid():
                        apply_layer_style(vlayer, LAYER_NAME_BDOT10K_DROGI)
                        self.project.addMapLayer(vlayer)
                        pushLogInfo("Dodano drogi.")
                
                if self.output_linie_path and os.path.exists(self.output_linie_path):
                    vlayer = QgsVectorLayer(self.output_linie_path, LAYER_NAME_BDOT10K_LINIE, "ogr")
                    if vlayer.isValid():
                        apply_layer_style(vlayer, LAYER_NAME_BDOT10K_LINIE)
                        self.project.addMapLayer(vlayer)
                        pushLogInfo("Dodano linie.")

                pushMessage(self.iface, "Pobrano dane BDOT.")
            else:
                pushWarning(self.iface, "Nie udało się pobrać danych")

        except Exception as e:
            pushLogInfo(f"BŁĄD w FINISHED: {e}")
            pushWarning(self.iface, "Błąd wtyczki")
        finally:
            self.analizaBtn.setEnabled(True)
            self.resetujBtn.setEnabled(True)

