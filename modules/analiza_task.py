# -*- coding: utf-8 -*-

from qgis.core import (
    QgsTask, QgsMessageLog, Qgis, QgsProject, QgsVectorLayer,
    QgsField, QgsGeometry, QgsPointXY, QgsPoint, QgsFeature,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsVectorLayerSimpleLabeling, QgsMapSettings, QgsRectangle
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import (
    LAYER_NAME_BDOT10K_DROGI, LAYER_NAME_BDOT10K_LINIE,
    OUTPUT_LAYERS, VOLTAGE_TYPES, ROAD_TYPE_FOREST,
    SOIL_ROLES, ATTR_GL, ATTR_ID_ADRES, 
    ATTR_RODZAJ_ORIGINAL, ATTR_NR_OB, ATTR_ADR_LES, 
    ATTR_POW, ATTR_ODL, ATTR_RODZAJ, LABEL_SETTINGS,
    LAYER_NAME_DROGI_LESNE_FILTER, ATTR_KOD, AREA_HA_THRESHOLD,
    LAYER_KEY_OBSZARY, LAYER_KEY_LINIE, LAYER_KEY_DROGI,
    RESULT_KEY_GEOMETRY, RESULT_KEY_AREA_HA, RESULT_KEY_ID,
    RESULT_KEY_NR_OB, RESULT_KEY_DIST, RESULT_KEY_RODZAJ,
    PROVIDER_MEMORY, URI_TEMPLATE_POLYGON, URI_TEMPLATE_LINE
)
from ..utils import pushLogInfo, pushMessage, pushWarning, apply_layer_style

class AnalizaTask(QgsTask):
   
    def __init__(self, description, wydzielenia_opisy, wydzielenia, oddzialy, drogi_lesne, mapa_bazowa, iface, raportBtn, wydrukBtn, analizaBtn, zapisBtn, resetujBtn):
        super().__init__(description, QgsTask.CanCancel)

        self.iface = iface
        self.raportBtn = raportBtn
        self.wydrukBtn = wydrukBtn
        self.zapisBtn = zapisBtn
        self.resetujBtn = resetujBtn
        self.analizaBtn = analizaBtn
        
        self.mapa_bazowa = mapa_bazowa
        
        self.exception = None
        self.result_data = None
        self.rodzaj_napiecia = VOLTAGE_TYPES

        # Wczytywanie danych
        pushLogInfo("AnalizaTask: Wczytywanie obiektów...")

        # Wydzielenia Opisy
        self.wydzielenia_opisy_feats = [f for f in wydzielenia_opisy.getFeatures()]
        pushLogInfo(f"AnalizaTask: Wczytano {len(self.wydzielenia_opisy_feats)} wydzielenia_opisy")
        
        # Wydzielenia
        self.wydzielenia_feats = [f for f in wydzielenia.getFeatures()]
        pushLogInfo(f"AnalizaTask: Wczytano {len(self.wydzielenia_feats)} wydzielenia")
        
        # Oddzialy
        self.oddzialy_feats = [f for f in oddzialy.getFeatures() if f.hasGeometry()]
        pushLogInfo(f"AnalizaTask: Wczytano {len(self.oddzialy_feats)} oddzialy")
        
        # Drogi Leśne
        # najpierw próba po nazwie, jeżeli inaczej się nazywa to po indeksie
        self.drogi_lesne_feats = []
        try:
            fields = drogi_lesne.fields()
            idx = fields.indexOf(ATTR_KOD)
            if idx == -1: idx = 1 # Fallback to 1
            
            count_total = 0
            for f in drogi_lesne.getFeatures():
                count_total += 1
                if f.hasGeometry():
                    val = f[idx]
                    if str(val) == LAYER_NAME_DROGI_LESNE_FILTER:
                       self.drogi_lesne_feats.append(f)
            
            pushLogInfo(f"AnalizaTask: Wczytano {len(self.drogi_lesne_feats)} drogi_lesne (z {count_total}) z filtrem {LAYER_NAME_DROGI_LESNE_FILTER}")
        except Exception as e:
            pushLogInfo(f"AnalizaTask Błąd wczytywania drogi_lesne: {e}")

        # warstwy BDOT
        project = QgsProject.instance()
        
        drogi_layers = project.mapLayersByName(LAYER_NAME_BDOT10K_DROGI)
        if drogi_layers:
            self.drogi_publiczne_feats = [f for f in drogi_layers[0].getFeatures() if f.hasGeometry()]
            pushLogInfo(f"AnalizaTask: Wczytano {len(self.drogi_publiczne_feats)} drogi_publiczne")
        else:
            self.drogi_publiczne_feats = None
            pushLogInfo("AnalizaTask: Warstwa BDOT Drogi NIE znaleziona")

        linie_layers = project.mapLayersByName(LAYER_NAME_BDOT10K_LINIE)
        if linie_layers:
            # Filtrowanie linii według rodzaju napięcia
            self.linie_feats = [f for f in linie_layers[0].getFeatures() 
                                if f.hasGeometry() and f[ATTR_RODZAJ_ORIGINAL] in self.rodzaj_napiecia]
            pushLogInfo(f"AnalizaTask: Wczytano {len(self.linie_feats)} linie")
        else:
            self.linie_feats = None
            pushLogInfo("AnalizaTask: Warstwa BDOT Linie NIE znaleziona")

    def run(self):
        """
        Przetwarzanie w tle. Używa załadowanych list obiektów.
        """
        pushLogInfo('Rozpoczęto wykonywanie AnalizaTask')
        
        try:
            # Pozwól na uruchomienie nawet przy pustych listach, aby zobaczyć logi, ale sprawdź istnienie
            if self.drogi_publiczne_feats is None:
                 pushLogInfo("Ostrzeżenie: drogi_publiczne_feats jest None")
            if self.linie_feats is None:
                 pushLogInfo("Ostrzeżenie: linie_feats jest None")
                 
            # Filtrowanie wydzielenia po klasie bonitacji
            valid_id_adres = set()
            for f in self.wydzielenia_opisy_feats:
                if self.isCanceled(): return False
                
                gl_val = str(f[ATTR_GL])
                for role in SOIL_ROLES:
                    if role in gl_val:
                        valid_id_adres.add(f[ATTR_ID_ADRES])
                        break
            
            if not valid_id_adres:
                pushLogInfo("Brak wydzieleń o wymaganej klasie bonitacji.")
                return False

            # Pobieranie geometrii dla valid IDs
            relevant_features = []
            for f in self.wydzielenia_feats:
                if self.isCanceled(): return False
                
                idf = f[ATTR_ID_ADRES]
                if idf in valid_id_adres:
                    relevant_features.append(f)
            
            if not relevant_features:
                pushLogInfo("Nie znaleziono odpowiednich obiektów dla poprawnych ID")
                return False

            # Operacje geometryczne: Union -> MultipartToSingle
            geometries = [f.geometry() for f in relevant_features]
            if not geometries: return False
            
            combined_geom = QgsGeometry.unaryUnion(geometries)
            
            if self.isCanceled(): return False

            single_parts = []
            if combined_geom.isMultipart():
                single_parts = combined_geom.asGeometryCollection()
            else:
                single_parts = [combined_geom]

            # Filtracja obszarów po powierzchni > 1.5 ha
            obszary_valid = []
            for i, geom in enumerate(single_parts):
                area_ha = geom.area() / 10000.0
                if area_ha > AREA_HA_THRESHOLD:
                    obszary_valid.append({
                        RESULT_KEY_GEOMETRY: geom,
                        RESULT_KEY_AREA_HA: round(area_ha, 2),
                        RESULT_KEY_ID: i+1
                    })

            if not obszary_valid:
                pushLogInfo(f"Brak obszarów > {AREA_HA_THRESHOLD}ha")
                return False
            
            pushLogInfo(f"Znaleziono {len(obszary_valid)} poprawnych obszarów > {AREA_HA_THRESHOLD}ha")

            # Określenie adresów (adr_les)
            for obszar in obszary_valid:
                if self.isCanceled(): return False
                
                contained_adresses = []
                geom_obszar = obszar[RESULT_KEY_GEOMETRY]
                
                for f in relevant_features:
                    if geom_obszar.boundingBox().intersects(f.geometry().boundingBox()):
                        if geom_obszar.contains(f.geometry()):
                            try:
                                adr = f[OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['attributes'][1]]
                            except KeyError:
                                adr = f[2]
                            contained_adresses.append(str(adr))
                
                obszar[OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['attributes'][1]] = '\n'.join(contained_adresses)

            # Analiza najbliższych linii i drog
            final_obszary = []
            final_lines = []
            final_roads = []

            for obszar in obszary_valid:
                if self.isCanceled(): return False
                
                centroid = obszar[RESULT_KEY_GEOMETRY].centroid()
                point_xy = QgsPointXY(centroid.asPoint())
                
                # najbliższa linia
                min_dist = float('inf')
                nearest_feat = None
                
                if self.linie_feats:
                    for lf in self.linie_feats:
                        dist_sqr, close_pt, _, _ = lf.geometry().closestSegmentWithContext(point_xy)
                        if dist_sqr < min_dist:
                            min_dist = dist_sqr
                            nearest_feat = lf
                
                if nearest_feat:
                    real_dist = min_dist ** 0.5
                    final_lines.append({
                        RESULT_KEY_NR_OB: obszar[RESULT_KEY_ID],
                        RESULT_KEY_DIST: real_dist,
                        RESULT_KEY_RODZAJ: self.rodzaj_napiecia.get(nearest_feat[ATTR_RODZAJ_ORIGINAL], 'unknown'),
                        RESULT_KEY_GEOMETRY: nearest_feat.geometry()
                    })
                
                # Drogi publiczne
                min_dist_pub = float('inf')
                nearest_pub = None
                nearest_pt_pub = None
                
                if self.drogi_publiczne_feats:
                    for df in self.drogi_publiczne_feats:
                        dist_sqr, close_pt, _, _ = df.geometry().closestSegmentWithContext(point_xy)
                        if dist_sqr < min_dist_pub:
                            min_dist_pub = dist_sqr
                            nearest_pub = df
                            nearest_pt_pub = close_pt
                        
                # Drogi leśne
                min_dist_for = float('inf')
                nearest_for = None
                nearest_pt_for = None
                
                if self.drogi_lesne_feats:
                    for df in self.drogi_lesne_feats:
                        dist_sqr, close_pt, _, _ = df.geometry().closestSegmentWithContext(point_xy)
                        if dist_sqr < min_dist_for:
                            min_dist_for = dist_sqr
                            nearest_for = df
                            nearest_pt_for = close_pt
                
                # Porównanie
                chosen_road = None
                chosen_dist = float('inf')
                chosen_type = ''
                chosen_geom = None
                
                dist_pub_real = min_dist_pub ** 0.5 if min_dist_pub != float('inf') else float('inf')
                dist_for_real = min_dist_for ** 0.5 if min_dist_for != float('inf') else float('inf')
                
                if dist_pub_real == float('inf') and dist_for_real == float('inf'):
                    pass
                elif dist_pub_real <= dist_for_real:
                    if nearest_pub:
                        chosen_dist = dist_pub_real
                        try:
                            chosen_type = nearest_pub[ATTR_RODZAJ_ORIGINAL]
                        except KeyError:
                            chosen_type = str(nearest_pub.attributes()[0])

                        chosen_geom = nearest_pub.geometry()
                        
                        is_forest = False
                        if self.oddzialy_feats:
                            for oddz in self.oddzialy_feats:
                                if nearest_pub.geometry().intersects(oddz.geometry()):
                                    is_forest = True
                                    break
                        if is_forest:
                            chosen_type = ROAD_TYPE_FOREST
                else:
                    if nearest_for:
                        chosen_dist = dist_for_real
                        chosen_type = ROAD_TYPE_FOREST
                        chosen_geom = nearest_for.geometry()

                if chosen_geom:
                    final_roads.append({
                        RESULT_KEY_NR_OB: obszar[RESULT_KEY_ID],
                        RESULT_KEY_DIST: chosen_dist,
                        RESULT_KEY_RODZAJ: chosen_type,
                        RESULT_KEY_GEOMETRY: chosen_geom
                    })
                
                # Dodaj finalny obszar do wyników
                final_obszary.append(obszar)

            self.result_data = {
                'obszary': final_obszary,
                'lines': final_lines,
                'roads': final_roads
            }
            pushLogInfo(f"AnalizaTask Zakończono analizę. Linie: {len(final_lines)}, Drogi: {len(final_roads)}")
            return True

        except Exception as e:
            self.exception = e
            pushLogInfo(f"AnalizaTask Wyjątek: {e}")
            return False

    def finished(self, result):
        if result and self.result_data:
            try:
                # Obszary
                self.obszary_layer = QgsVectorLayer(URI_TEMPLATE_POLYGON, OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['name'], PROVIDER_MEMORY)
                pr = self.obszary_layer.dataProvider()
                self.obszary_layer.startEditing()
                
                pr.addAttributes([
                    QgsField(ATTR_NR_OB, QVariant.Int),
                    QgsField(ATTR_ADR_LES, QVariant.String),
                    QgsField(ATTR_POW, QVariant.Double, len=10, prec=2)
                ])
                self.obszary_layer.updateFields()
                
                feats = []
                for item in self.result_data['obszary']:
                    f = QgsFeature()
                    f.setGeometry(item[RESULT_KEY_GEOMETRY])
                    f.setAttributes([item[RESULT_KEY_ID], item[OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['attributes'][1]], item[RESULT_KEY_AREA_HA]])
                    feats.append(f)
                pr.addFeatures(feats)
                self.obszary_layer.commitChanges()
                
                # Stylizacja Obszary
                apply_layer_style(self.obszary_layer, OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['name'])
                
                # Etykiety
                ls = QgsPalLayerSettings()
                tf = QgsTextFormat()
                tf.setFont(QFont(LABEL_SETTINGS['font_family'], LABEL_SETTINGS['font_size']))
                color_parts = [int(x.strip()) for x in LABEL_SETTINGS['color_rgb'].split(',')]
                tf.setColor(QColor(*color_parts))
                
                bs = QgsTextBufferSettings()
                bs.setEnabled(True)
                bs.setSize(LABEL_SETTINGS['buffer_size'])
                tf.setBuffer(bs)
                
                ls.setFormat(tf)
                ls.fieldName = ATTR_NR_OB
                ls.xOffset = LABEL_SETTINGS['x_offset']
                ls.yOffset = LABEL_SETTINGS['y_offset']
                ls.enabled = True
                
                self.obszary_layer.setLabeling(QgsVectorLayerSimpleLabeling(ls))
                self.obszary_layer.setLabelsEnabled(True)

                QgsProject.instance().addMapLayer(self.obszary_layer)

                # Linie
                self.linie_layer = QgsVectorLayer(URI_TEMPLATE_LINE, OUTPUT_LAYERS[LAYER_KEY_LINIE]['name'], PROVIDER_MEMORY)
                pr = self.linie_layer.dataProvider()
                self.linie_layer.startEditing()
                pr.addAttributes([
                    QgsField(ATTR_NR_OB, QVariant.Int),
                    QgsField(ATTR_ODL, QVariant.Double, len=10, prec=2),
                    QgsField(ATTR_RODZAJ, QVariant.String)
                ])
                self.linie_layer.updateFields()
                
                feats = []
                for item in self.result_data['lines']:
                    f = QgsFeature()
                    f.setGeometry(item[RESULT_KEY_GEOMETRY])
                    f.setAttributes([item[RESULT_KEY_NR_OB], item[RESULT_KEY_DIST], item[RESULT_KEY_RODZAJ]])
                    feats.append(f)
                pr.addFeatures(feats)
                self.linie_layer.commitChanges()
                
                # Stylizacja Linie
                apply_layer_style(self.linie_layer, OUTPUT_LAYERS[LAYER_KEY_LINIE]['name'])
                QgsProject.instance().addMapLayer(self.linie_layer)

                # Drogi
                self.drogi_layer = QgsVectorLayer(URI_TEMPLATE_LINE, OUTPUT_LAYERS[LAYER_KEY_DROGI]['name'], PROVIDER_MEMORY)
                pr = self.drogi_layer.dataProvider()
                self.drogi_layer.startEditing()
                pr.addAttributes([
                    QgsField(ATTR_NR_OB, QVariant.Int),
                    QgsField(ATTR_ODL, QVariant.Double, len=10, prec=2),
                    QgsField(ATTR_RODZAJ, QVariant.String)
                ])
                self.drogi_layer.updateFields()
                
                feats = []
                for item in self.result_data['roads']:
                    f = QgsFeature()
                    f.setGeometry(item[RESULT_KEY_GEOMETRY])
                    f.setAttributes([item[RESULT_KEY_NR_OB], item[RESULT_KEY_DIST], item[RESULT_KEY_RODZAJ]])
                    feats.append(f)
                pr.addFeatures(feats)
                self.drogi_layer.commitChanges()
                
                # Stylizacja Drogi
                apply_layer_style(self.drogi_layer, OUTPUT_LAYERS[LAYER_KEY_DROGI]['name'])
                QgsProject.instance().addMapLayer(self.drogi_layer)
                
                # Aktualizacja widoczności
                layers_to_show = [self.obszary_layer.id(), self.linie_layer.id(), self.drogi_layer.id(), self.mapa_bazowa.id()]
                root = QgsProject.instance().layerTreeRoot()
                for child in root.children():
                    if child.layerId() not in layers_to_show:
                        child.setItemVisibilityChecked(False)
                    else:
                        child.setItemVisibilityChecked(True)
                
                # Przybliżenie
                extent = self.obszary_layer.extent()
                if extent.isEmpty():
                    return
                extent.grow(extent.width() * 0.1)
                self.iface.mapCanvas().setExtent(extent)
                self.iface.mapCanvas().refresh()

                pushMessage(self.iface, "Analiza zakończona sukcesem")

                # Włącz przyciski
                self.raportBtn.setEnabled(True)
                self.wydrukBtn.setEnabled(True)
                self.zapisBtn.setEnabled(True)
                self.resetujBtn.setEnabled(True)

            except Exception as e:
                pushLogInfo(f"Błąd w finished: {e}")
                pushWarning(self.iface, "Błąd podczas tworzenia warstw wynikowych.")
                if self.exception: 
                    raise self.exception
                else: 
                     raise e

        else:
            if self.exception:
                pushWarning(self.iface, f"Błąd analizy: {self.exception}")
            else:
                pushWarning(self.iface, "Brak wyników analizy lub zadanie anulowano.")
            
            self.resetujBtn.setEnabled(True)
            self.analizaBtn.setEnabled(True)

    def cancel(self):
        pushLogInfo('AnalizaTask anulowane')
        super().cancel()