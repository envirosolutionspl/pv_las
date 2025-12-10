# -*- coding: utf-8 -*-

import processing
from operator import itemgetter

from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QMetaType

from qgis.core import (
    QgsTask, 
    QgsMessageLog, 
    Qgis, 
    QgsVectorLayer, 
    QgsField, 
    QgsProject, 
    QgsSingleSymbolRenderer, 
    QgsFillSymbol, 
    QgsLineSymbol, 
    QgsGeometry, 
    QgsPointXY, 
    QgsPoint, 
    QgsPalLayerSettings, 
    QgsTextFormat, 
    QgsTextBufferSettings, 
    QgsVectorLayerSimpleLabeling, 
    QgsMapSettings, 
    QgsRectangle,
    QgsFeature
)

from .. import constants


class AnalizaTask(QgsTask):
   
    def __init__(self, description, wydzielenia_opisy, wydzielenia, oddzialy, drogi_lesne, mapa_bazowa, iface, raportBtn, wydrukBtn, analizaBtn, zapisBtn, resetujBtn):
       
        super().__init__(description, QgsTask.CanCancel)

        self.wydzielenia_opisy = wydzielenia_opisy
        self.wydzielenia = wydzielenia
        self.oddzialy = oddzialy
        self.drogi_lesne = drogi_lesne
        self.mapa_bazowa = mapa_bazowa
        self.raportBtn = raportBtn
        self.wydrukBtn = wydrukBtn
        self.zapisBtn = zapisBtn
        self.resetujBtn = resetujBtn
        self.iface=iface
        self.analizaBtn = analizaBtn
        self.exception = None

        self.exception = None

        self.rodzaj_napiecia = constants.VOLTAGE_TYPES

           
  
    def run(self):

        QgsMessageLog.logMessage('Started task')
        QgsMessageLog.logMessage('wykonuję analizę')
        self.analizaBtn.setEnabled(False)
        self.resetujBtn.setEnabled(False)

        # wybiera wydzielenia równe i ponizej IV klasy bonitacji gleby
        r_features = []
        features = list(self.wydzielenia_opisy.getFeatures())
        roles = constants.SOIL_ROLES
        
        for feature in features:
            # sprawdzenie czy role znajduje się w atrybucie g_l
            gl_value = str(feature[constants.ATTR_GL])
            if any(role in gl_value for role in roles):
                r_features.append(feature)
        
        if r_features:
            r_features_ids = {f[constants.ATTR_ID_ADRES] for f in r_features}
            
            features2 = self.wydzielenia.getFeatures()
            # filtruje tylko te obiekty ktorych id_adres znajduje się w r_features_ids
            all_features = [f for f in features2 if f[constants.ATTR_ID_ADRES] in r_features_ids]
            
            wydzielenia_po_analizie = QgsVectorLayer(
                    'Polygon?crs=epsg:2180', constants.LAYER_NAME_WYDZIELENIA_PO_ANALIZIE, 'memory')
            pr = wydzielenia_po_analizie.dataProvider()
            wydzielenia_po_analizie.startEditing()

            pr.addFeatures(all_features)
            wydzielenia_po_analizie.commitChanges()
        else:
            QMessageBox.critical(None, "Nie ma wydzieleń o wymaganej klasie bonitacji gleby", "Analiza zakończona")
            self.resetujBtn.setEnabled(True)
            return False


        # łączenie sąsiednie wydzielenia w o wymaganej klasie bonitacji i wybór obszarów o pow. powyżej 1.5 ha
        wydzielenia_po_analizie_polaczone = processing.run("qgis:buffer", {'INPUT': wydzielenia_po_analizie, 'DISTANCE':0, 'DISSOLVE':True, 'OUTPUT': 'memory:'})['OUTPUT']
        wydzielenia_po_analizie_polaczone_w_obszary = processing.run("native:multiparttosingleparts", {'INPUT': wydzielenia_po_analizie_polaczone,'OUTPUT': 'memory:'})['OUTPUT']
        self.obszary = QgsVectorLayer('Polygon?crs=epsg:2180', constants.RESULT_LAYER_OBSZARY, 'memory')
        pr = self.obszary.dataProvider()
        self.obszary.startEditing()
        pr.addAttributes([QgsField(constants.ATTR_NR_OB, QMetaType.Int),
                          QgsField(constants.ATTR_ADR_LES, QMetaType.QString),
                        QgsField(constants.ATTR_POW, QMetaType.Double)]
                          )
        obszary_powyzej_poltora_ha= [feature for feature in wydzielenia_po_analizie_polaczone_w_obszary.getFeatures() if round((feature.geometry().area()/10000)>1.5, 2)]
        for i, obszar_powyzej_poltora_ha in enumerate (obszary_powyzej_poltora_ha):
            adr_les=[feature[2] for feature in all_features if obszar_powyzej_poltora_ha.geometry().contains(feature.geometry())]

            obszar_powyzej_poltora_ha.setAttributes([i+1, ('\n').join(adr_les), round(obszar_powyzej_poltora_ha.geometry().area()/10000, 2)])
            pr.addFeatures([obszar_powyzej_poltora_ha])

        self.obszary.commitChanges()
        obszary= [feature for feature in self.obszary.getFeatures()]

        if len(obszary)>0:
           
            # dodanie stylu do warstwy wyznaczone obszary
            symbol =  QgsFillSymbol.createSimple(
                {'color': constants.STYLE_COLOR_WYDZIELENIA, 'outline_color' : constants.STYLE_COLOR_WYDZIELENIA_OUTLINE,  'outline_style':'solid',
            'outline_width': constants.STYLE_WIDTH_WYDZIELENIA})
            renderer = QgsSingleSymbolRenderer(symbol)
            self.obszary.setRenderer(renderer)
            QgsProject.instance().addMapLayer(self.obszary)

             # wyznaczenie najbliższych dróg i linii energetycznych do wyznaczonych obszarów

            centroids = processing.run("native:centroids", {'INPUT': self.obszary,'ALL_PARTS':False,'OUTPUT':'memory:'})['OUTPUT']
            self.linie_bdot10k = QgsProject.instance().mapLayersByName(constants.LAYER_NAME_BDOT10K_LINIE)[0]
            lines = [feature for feature in self.linie_bdot10k.getFeatures() if feature[37] in self.rodzaj_napiecia.keys()]
            self.linie = QgsVectorLayer('LineString?crs=epsg:2180', constants.RESULT_LAYER_LINIE, 'memory')

            # dodanie stylu do warstwy wyznaczone z najbliższymi liniami energetycznymi
            symbol =  QgsLineSymbol.createSimple(
                {'color': constants.STYLE_COLOR_LINIE_ENERGETYCZNE, 'outline_color' : constants.STYLE_COLOR_LINIE_ENERGETYCZNE,  'outline_style': 'solid',
            'outline_width': constants.STYLE_WIDTH_LINIE_ENERGETYCZNE})
            renderer = QgsSingleSymbolRenderer(symbol)
            self.linie.setRenderer(renderer)
            
           
            QgsProject.instance().addMapLayer(self.linie)
            prov = self.linie.dataProvider()
            prov.addAttributes( [ QgsField(constants.ATTR_NR_OB, QMetaType.Int), QgsField(constants.ATTR_ODL, QMetaType.Int), QgsField(constants.ATTR_RODZAJ, QMetaType.QString)])
            for i, points in enumerate(centroids.getFeatures()):
                cswc = min([(l.id(),l.geometry().closestSegmentWithContext(QgsPointXY(points.geometry().asPoint()))) for l in lines], key=itemgetter(1))
                minDistPoint = cswc[1][1]  
                minDistLine = cswc[0]      
                feat = QgsFeature() 
                line = QgsGeometry.fromPolyline([QgsPoint(points.geometry().asPoint()), QgsPoint(minDistPoint[0], minDistPoint[1])]) 
                feat= self.linie_bdot10k.getFeature(minDistLine)
                feat.setAttributes([points[constants.ATTR_NR_OB], line.length(), self.rodzaj_napiecia[feat[37]]])
                prov.addFeatures([feat])
            self.linie.triggerRepaint()
            self.linie.updateFields()


            self.drogi_bdot10k = QgsProject.instance().mapLayersByName(constants.LAYER_NAME_BDOT10K_DROGI)[0]
            drogi = [ft for ft in self.drogi_bdot10k.getFeatures() if ft.geometry().isGeosValid()]
            oddzialy = [feature for feature in self.oddzialy.getFeatures() if feature.geometry().isGeosValid()]
            drogi_lesne = [feature for feature in self.drogi_lesne.getFeatures() if feature[1] ==constants.LAYER_NAME_DROGI_LESNE_FILTER and feature.geometry().isGeosValid()]
            self.drogi = QgsVectorLayer('LineString?crs=epsg:2180', constants.RESULT_LAYER_DROGI, 'memory')
            
            prov = self.drogi.dataProvider()
            prov.addAttributes( [ QgsField(constants.ATTR_NR_OB, QMetaType.Int), QgsField(constants.ATTR_ODL, QMetaType.Int), QgsField(constants.ATTR_RODZAJ,QMetaType.QString)])
            # dodanie stylu do warstwy wyznaczone z najbliższymi drogami
            symbol =  QgsLineSymbol.createSimple(
                {'color': constants.STYLE_COLOR_DROGI, 'outline_color' : constants.STYLE_COLOR_DROGI,  'outline_style': 'solid',
            'outline_width': constants.STYLE_WIDTH_DROGI})
            renderer = QgsSingleSymbolRenderer(symbol)
            self.drogi.setRenderer(renderer)
            QgsProject.instance().addMapLayer(self.drogi)

            for i, points in enumerate(centroids.getFeatures()):
                cswc1 = min([(l.id(),l.geometry().closestSegmentWithContext(QgsPointXY(points.geometry().asPoint()))) for l in drogi], key=itemgetter(1))
                minDistPoint1 = cswc1[1][1] 
                minDistLine1 = cswc1[0]   
                line1 = QgsGeometry.fromPolyline([QgsPoint(points.geometry().asPoint()), QgsPoint(minDistPoint1[0], minDistPoint1[1])]) 
                length1 = line1.length()

                cswc2 = min([(l.id(),l.geometry().closestSegmentWithContext(QgsPointXY(points.geometry().asPoint()))) for l in drogi_lesne], key=itemgetter(1))
                minDistPoint2 = cswc2[1][1]  
                minDistLine2 = cswc2[0]    
                line2 = QgsGeometry.fromPolyline([QgsPoint(points.geometry().asPoint()), QgsPoint(minDistPoint2[0], minDistPoint2[1])]) 
                length2 = line2.length()
                if  length1 <  length2:
                    feat= self.drogi_bdot10k.getFeature(minDistLine1)
                    a=feat[37]

                    for i, feature112 in enumerate(oddzialy):
                        if feat.geometry().intersects(feature112.geometry()):
                            feat.setAttributes([points[constants.ATTR_NR_OB], length1, 'leśna'])
                            break
                        else: 
                            feat.setAttributes([points[constants.ATTR_NR_OB], length1, a])  
                    prov.addFeatures([feat])
                else:
                    feat= self.drogi_lesne.getFeature(minDistLine2)
                    feat.setAttributes([points[constants.ATTR_NR_OB], length2, 'leśna'])
                    prov.addFeatures([feat])
            self.drogi.triggerRepaint()
            self.drogi.updateFields()
            
           # dodanie etykiet (nr obszaru) do warstwy z wyznaczonymi obszarami
            layer_settings  = QgsPalLayerSettings()
            text_format = QgsTextFormat()
            text_format.setFont(QFont(constants.LABEL_FONT_FAMILY, constants.LABEL_FONT_SIZE))
            text_format.setSize(constants.LABEL_FONT_SIZE)
            text_format.setColor(QColor(constants.LABEL_COLOR_RGB))
            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)
            buffer_settings.setSize(0.10)
            text_format.setBuffer(buffer_settings)
            layer_settings.setFormat(text_format)
            layer_settings.fieldName = constants.ATTR_NR_OB
            layer_settings.xOffset = 2.0
            layer_settings.yOffset = 3.0
            layer_settings.enabled = True
            layer_settings.displayAll = True
            labelig = QgsVectorLayerSimpleLabeling(layer_settings)
            self.obszary.setLabelsEnabled(True)
            self.obszary.setLabeling(labelig)
            self.obszary.triggerRepaint()

            # ustawienie do zakresu warst: wyznaczone obszary, najbliższe linie energetycze, najbliższe drogi, mapa bazowa
            # wyłączenie widoczności innych warstw 
                       
            obszary_id = self.obszary.id()
            drogi_id = self.drogi.id()
            linie_id = self.linie.id()
            base_map_id = self.mapa_bazowa.id()
            layers_id = [obszary_id, drogi_id, linie_id, base_map_id]                   
            root = QgsProject.instance().layerTreeRoot()
            allLayers = root.layerOrder()
            for layer in allLayers:
                if layer.id() not in layers_id:
                    root.findLayer(layer.id()).setItemVisibilityChecked(False)
                    
            layers=[self.obszary, self.drogi, self.linie]
            ms = QgsMapSettings()
            ms.setLayers(layers)  
            rect = QgsRectangle(ms.fullExtent())
            self.iface.mapCanvas().setExtent(rect)
            self.raportBtn.setEnabled(True)
            self.wydrukBtn.setEnabled(True)
            self.zapisBtn.setEnabled(True)
            self.resetujBtn.setEnabled(True)
        else:
            msg = QMessageBox.critical(None, "Nie ma wydzieleń spełniających wymagania", "Analiza zakończona")
            return False

                       
        if self.isCanceled():
            return False
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
                                                "Analiza nie została wykonana.")

    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
            
      
        
