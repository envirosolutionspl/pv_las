# -*- coding: utf-8 -*-


import tempfile
import zipfile
import requests
import io
import os
import processing
from ..constants import (
    BDOT10K_SHP_URL_TEMPLATE, BDOT_FILE_SUFFIX_DROGI, BDOT_FILE_SUFFIX_LINIE,
    LAYER_NAME_BDOT10K_DROGI, LAYER_NAME_BDOT10K_LINIE, CRS_EPSG_2180,
    STYLE_COLOR_BDOT_DROGI, STYLE_WIDTH_BDOT_DROGI,
    STYLE_COLOR_BDOT_LINIE, STYLE_WIDTH_BDOT_LINIE
)
from ..utils import pushLogInfo

from qgis.core import (
    QgsTask, 
    QgsMessageLog, 
    Qgis, 
    QgsVectorLayer, 
    QgsLineSymbol, 
    QgsSingleSymbolRenderer, 
    QgsProject
)

class PobierzBdotTask(QgsTask):
   

    def __init__(self, description, drogi_layer, linie_layer, features, drogi_list, linie_list, iface, wczytajBdot10kBtn, analizaBtn, resetujBtn):
       
        super().__init__(description, QgsTask.CanCancel)

        self.drogi_bdot10k = drogi_layer
        self.linie_bdot10k=linie_layer
        self.features = features 
        self.drogi_list = drogi_list
        self.linie_list=linie_list
        self.iface=iface
        self.wczytajBdot10kBtn = wczytajBdot10kBtn
        self.resetujBtn = resetujBtn
        self.analizaBtn = analizaBtn
        self.exception = None
  
    def run(self):

        pushLogInfo('Started task')
        pushLogInfo('pobieram bdot10k')
        self.wczytajBdot10kBtn.setEnabled(False)
        self.resetujBtn.setEnabled(False)

        # pobieranie dróg i linii bdot10k z określonych powiatów
        tempdir = tempfile.TemporaryDirectory()
        for i, feature in enumerate(self.features):
            r = requests.get(BDOT10K_SHP_URL_TEMPLATE.format(feature[1], feature[1]+feature[2]))
            z = zipfile.ZipFile(io.BytesIO(r.content))
            
            extract_path = os.path.join(tempdir.name, str(i))
            z.extractall(extract_path)
          
            for root, dirs, files in os.walk(extract_path):
                for file in files:
               
                    if file.endswith(BDOT_FILE_SUFFIX_DROGI):
                        
                        path = os.path.join(root, file)
                        ddd = QgsVectorLayer(path, LAYER_NAME_BDOT10K_DROGI, "ogr")
                        self.drogi_list.append(ddd)


                    if file.endswith(BDOT_FILE_SUFFIX_LINIE):
                        path = os.path.join(root, file)
                        ddd = QgsVectorLayer(path, LAYER_NAME_BDOT10K_LINIE, "ogr")
                        self.linie_list.append(ddd)

        # łączenie dróg i linii z określonch dróg i powiatów w pojedyncze warsty 

        parameters = {'LAYERS': self.drogi_list, 
              'CRS': CRS_EPSG_2180, 
              'OUTPUT': 'memory:'}

        drogi_polaczone=processing.run("native:mergevectorlayers", parameters)['OUTPUT']
        

        parameters = {'LAYERS': self.linie_list, 
                'CRS': CRS_EPSG_2180, 
                'OUTPUT': 'memory:'}
        linie_polaczone=processing.run("qgis:mergevectorlayers", parameters)['OUTPUT']
        self.drogi_bdot10k = QgsVectorLayer('LineString?crs=epsg:2180', LAYER_NAME_BDOT10K_DROGI, 'memory')
        self.drogi_bdot10k.startEditing()
        pr = self.drogi_bdot10k.dataProvider()
        attr = drogi_polaczone.dataProvider().fields().toList()
        pr.addAttributes(attr)
        self.drogi_bdot10k.updateFields()
        pr.addFeatures(drogi_polaczone.getFeatures()) 
        self.drogi_bdot10k.commitChanges()

        # dodanie stylu do warstwy z drogami
        symbol =  QgsLineSymbol.createSimple(
                {'color': STYLE_COLOR_BDOT_DROGI, 'outline_color' : STYLE_COLOR_BDOT_DROGI,  'outline_style': 'solid',
            'outline_width': STYLE_WIDTH_BDOT_DROGI})
        renderer = QgsSingleSymbolRenderer(symbol)
        self.drogi_bdot10k.setRenderer(renderer)

        QgsProject.instance().addMapLayer(self.drogi_bdot10k)
        self.linie_bdot10k = QgsVectorLayer('LineString?crs=epsg:2180', LAYER_NAME_BDOT10K_LINIE, 'memory')
        self.linie_bdot10k.startEditing()
        pr = self.linie_bdot10k.dataProvider()
        attr = linie_polaczone.dataProvider().fields().toList()
        pr.addAttributes(attr)
        self.linie_bdot10k.updateFields()
        pr.addFeatures(linie_polaczone.getFeatures()) 
        self.linie_bdot10k.commitChanges()

        # dodanie stylu do warstwy z liniami energetycznymi
        symbol =  QgsLineSymbol.createSimple(
                {'color': STYLE_COLOR_BDOT_LINIE, 'outline_color' : STYLE_COLOR_BDOT_LINIE,  'outline_style': 'solid',
            'outline_width': STYLE_WIDTH_BDOT_LINIE})
        renderer = QgsSingleSymbolRenderer(symbol)
        self.linie_bdot10k.setRenderer(renderer)
        QgsProject.instance().addMapLayer(self.linie_bdot10k)
        self.wczytajBdot10kBtn.setEnabled(False)
        self.analizaBtn.setEnabled(True)

        if self.isCanceled():
            return False
        self.analizaBtn.setEnabled(True)
        self.resetujBtn.setEnabled(True)
        return True
    
    def finished(self, result):
        if result:
            pass  
        else:
            if self.exception is None:
                pushLogInfo('finished with false')
            else:
                pushLogInfo("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        pushLogInfo('cancel')
        super().cancel()
            
        
