# -*- coding: utf-8 -*-


import tempfile
import zipfile
import requests
import io
import os
import processing

from qgis.core import *

from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
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

        QgsMessageLog.logMessage('Started task')
        QgsMessageLog.logMessage('pobieram bdot10k')
        self.wczytajBdot10kBtn.setEnabled(False)
        self.resetujBtn.setEnabled(False)

        #pobieranie dróg i linii bdot10k z określonych powiatów
        for feature in self.features:
            r = requests.get('https://opendata.geoportal.gov.pl/bdot10k/SHP/{}/{}_SHP.zip'.format(feature[1], feature[1]+feature[2]))
            z = zipfile.ZipFile(io.BytesIO(r.content))
            tempdir = tempfile.TemporaryDirectory()
            z.extractall(tempdir.name)
          
            for root, dirs, files in os.walk(tempdir.name):
                for file in files:
               
                    if file.endswith('SKDR_L.shp'):
                        
                        path=tempdir.name + '\\'+ file
                        ddd = QgsVectorLayer(path, "drogi_bdot10k", "ogr")
                        self.drogi_list.append(ddd)


                    if file.endswith('SULN_L.shp'):
                        path=tempdir.name + '\\'+ file
                        ddd = QgsVectorLayer(path, "linie_bdot10k", "ogr")
                        self.linie_list.append(ddd)

        #łączenie dróg i linii z określonch dróg i powiatów w pojedyncze warsty 

        parameters = {'LAYERS': self.drogi_list, 
              'CRS': 'EPSG:2180', 
              'OUTPUT': 'memory:'}

        drogi_polaczone=processing.run("native:mergevectorlayers", parameters)['OUTPUT']
        

        parameters = {'LAYERS': self.linie_list, 
                'CRS': 'EPSG:2180', 
                'OUTPUT': 'memory:'}
        linie_polaczone=processing.run("qgis:mergevectorlayers", parameters)['OUTPUT']
        self.drogi_bdot10k = QgsVectorLayer('LineString?crs=epsg:2180', 'drogi_bdot10k', 'memory')
        self.drogi_bdot10k.startEditing()
        pr = self.drogi_bdot10k.dataProvider()
        attr = drogi_polaczone.dataProvider().fields().toList()
        pr.addAttributes(attr)
        self.drogi_bdot10k.updateFields()
        pr.addFeatures(drogi_polaczone.getFeatures()) 
        self.drogi_bdot10k.commitChanges()

        # dodanie stylu do warstwy z drogami
        symbol =  QgsLineSymbol.createSimple(
                {'color': 'gray', 'outline_color' : 'gray',  'outline_style': 'solid',
            'outline_width': '0.26'})
        renderer = QgsSingleSymbolRenderer(symbol)
        self.drogi_bdot10k.setRenderer(renderer)

        QgsProject.instance().addMapLayer(self.drogi_bdot10k)
        self.linie_bdot10k = QgsVectorLayer('LineString?crs=epsg:2180', 'linie_bdot10k', 'memory')
        self.linie_bdot10k.startEditing()
        pr = self.linie_bdot10k.dataProvider()
        attr = linie_polaczone.dataProvider().fields().toList()
        pr.addAttributes(attr)
        self.linie_bdot10k.updateFields()
        pr.addFeatures(linie_polaczone.getFeatures()) 
        self.linie_bdot10k.commitChanges()

        # dodanie stylu do warstwy z liniami energetycznymi
        symbol =  QgsLineSymbol.createSimple(
                {'color': 'red', 'outline_color' : 'red',  'outline_style': 'solid',
            'outline_width': '0.26'})
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
                QgsMessageLog.logMessage('finished with false')
            else:
                QgsMessageLog.logMessage("exception")
                raise self.exception
            self.iface.messageBar().pushWarning("Błąd",
                                                "Dane BDOT10k nie zostały pobrane.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
            
        
