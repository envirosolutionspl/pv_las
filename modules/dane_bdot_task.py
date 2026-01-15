# -*- coding: utf-8 -*-

import zipfile
import io
import os
from typing import List, Tuple, Optional

from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.PyQt.QtCore import QUrl
from qgis.core import (
    QgsTask, QgsBlockingNetworkRequest, QgsVectorLayer, 
    QgsProject, Qgis
)
import processing

from ..constants import (
    BDOT10K_SHP_URL_TEMPLATE, BDOT_FILE_SUFFIX_DROGI, BDOT_FILE_SUFFIX_LINIE,
    LAYER_NAME_BDOT10K_DROGI, LAYER_NAME_BDOT10K_LINIE, CRS_EPSG,
    PROVIDERS
)
from ..utils import Utils

class PobierzBdotTask(QgsTask):

    def __init__(self, description, features, iface, temp_path, 
                 wczytajBdot10kBtn, analizaBtn, resetujBtn, parent):
        super().__init__(description, QgsTask.CanCancel)
        
        self.parent = parent
        self.project = parent.project
        self.temp_dir_path = temp_path
        self.features = features 
        self.iface = iface
        
        # Przyciski UI
        self.wczytajBdot10kBtn = wczytajBdot10kBtn
        self.resetujBtn = resetujBtn
        self.analizaBtn = analizaBtn
        
        self.exception: Optional[Exception] = None
        self.output_drogi_path: Optional[str] = None
        self.output_linie_path: Optional[str] = None

    def run(self):
        """Logika działająca w tle."""
        Utils.pushLogInfo(f'Start PobierzBdotTask. Temp: {self.temp_dir_path}')
        
        # Pobieranie i wypakowywanie plików
        drogi_files, linie_files = self._downloadAndExtractAll()
        
        if self.isCanceled(): return False

        # Łączenie warstw
        if drogi_files:
            self.output_drogi_path = self._mergeBdotFiles(drogi_files, 'merged_drogi.gpkg')
        
        if linie_files:
            self.output_linie_path = self._mergeBdotFiles(linie_files, 'merged_linie.gpkg')
        
        return True

    def finished(self, result):
        """Logika działająca w głównym wątku."""
        if result:
            # Dodawanie warstw do projektu
            self._loadAndStyleLayer(self.output_drogi_path, LAYER_NAME_BDOT10K_DROGI)
            self._loadAndStyleLayer(self.output_linie_path, LAYER_NAME_BDOT10K_LINIE)
            
            # Walidacja wczytanych warstw
            drogi_layer = Utils.getLayerByName(LAYER_NAME_BDOT10K_DROGI, self.project)
            linie_layer = Utils.getLayerByName(LAYER_NAME_BDOT10K_LINIE, self.project)
            
            valid_drogi = drogi_layer is not None and drogi_layer.isValid() and drogi_layer.featureCount() > 0
            valid_linie = linie_layer is not None and linie_layer.isValid() and linie_layer.featureCount() > 0
            
            if not valid_drogi or not valid_linie:
                Utils.pushMessage(self.iface, "Błąd: Nie pobrano poprawnie danych BDOT10k lub dane dla tego obszaru są puste. Spróbuj pobrać ponownie.")
                self.analizaBtn.setEnabled(False)
                self.wczytajBdot10kBtn.setEnabled(True)
                self.resetujBtn.setEnabled(True)
                return

            Utils.pushMessage(self.iface, "Pobrano i wczytano dane BDOT10k.")
            self.analizaBtn.setEnabled(True)
            self.resetujBtn.setEnabled(True)
            self.wczytajBdot10kBtn.setEnabled(False)
        else:
            Utils.pushWarning(self.iface, "Nie udało się pobrać danych.")
            self.analizaBtn.setEnabled(False)
            self.resetujBtn.setEnabled(True)
            self.wczytajBdot10kBtn.setEnabled(True)

    # --- FUNKCJE POMOCNICZE ---

    def _downloadAndExtractAll(self) -> Tuple[List[str], List[str]]:
        """Pobiera ZIPy dla wszystkich powiatów i zwraca listy ścieżek do plików SHP."""
        drogi: List[str] = []
        linie: List[str] = []

        for i, feature in enumerate(self.features):
            if self.isCanceled(): break
            
            url = BDOT10K_SHP_URL_TEMPLATE.format(feature[1], feature[1] + feature[2])
            
            content = self._downloadFile(url)
            if not content:
                continue

            extract_path = os.path.join(self.temp_dir_path, str(i))
            d_files, l_files = self._extractSpecificFiles(content, extract_path)
            
            drogi.extend(d_files)
            linie.extend(l_files)

        return drogi, linie

    def _downloadFile(self, url: str) -> Optional[bytes]:
        """Pobiera pojedynczy plik z sieci."""
        request = QgsBlockingNetworkRequest()
        request.get(QNetworkRequest(QUrl(url)))
        reply = request.reply()
        
        if reply.error() != QNetworkReply.NetworkError.NoError:
            Utils.pushLogInfo(f"Błąd sieci ({url}): {reply.errorString()}")
            return None
        return reply.content()

    def _extractSpecificFiles(self, content: bytes, extract_to: str) -> Tuple[List[str], List[str]]:
        """Wypakowuje ZIP i segreguje pliki drogi/linie."""
        d_list, l_list = [], []
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                z.extractall(extract_to)
            
            for root, _, files in os.walk(extract_to):
                for file in files:
                    full_path = os.path.join(root, file)
                    if file.endswith(BDOT_FILE_SUFFIX_DROGI):
                        d_list.append(full_path)
                    elif file.endswith(BDOT_FILE_SUFFIX_LINIE):
                        l_list.append(full_path)
        except Exception as e:
            Utils.pushLogInfo(f"Błąd wypakowywania: {e}")
            
        return d_list, l_list

    def _mergeBdotFiles(self, files: List[str], output_filename: str) -> Optional[str]:
        """Łączy wiele plików SHP w jeden plik GeoPackage."""
        try:
            out_path = os.path.join(self.temp_dir_path, output_filename)
            params = {
                'LAYERS': files, 
                'CRS': f"EPSG:{CRS_EPSG}", 
                'OUTPUT': out_path
            }
            processing.run("native:mergevectorlayers", params)
            return out_path if os.path.exists(out_path) else None
        except Exception as e:
            Utils.pushLogInfo(f"Błąd Merge ({output_filename}): {e}")
            return None

    # -- Funkcje pomocnicze do finished --

    def _loadAndStyleLayer(self, path: Optional[str], layer_name: str) -> None:
        """Wczytuje warstwę do projektu i nakłada styl."""
        if not path or not os.path.exists(path):
            return

        vlayer = QgsVectorLayer(path, layer_name, PROVIDERS['OGR'])
        if vlayer.isValid():
            Utils.applyLayerStyle(vlayer, layer_name)
            self.project.addMapLayer(vlayer)
            Utils.pushLogInfo(f"Poprawnie wczytano warstwę: {layer_name}")
        else:
            Utils.pushLogInfo(f"Błąd walidacji warstwy: {layer_name}")