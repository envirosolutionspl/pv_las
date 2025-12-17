# =============================================================================
# Zmienne systemowe i globalne
# =============================================================================

# Adres URL kanału informacyjnego QGIS
FEED_URL = 'https://qgisfeed.envirosolutions.pl/'

# Katalog tymczasowy
TEMP_DIR_PREFIX = 'fotowoltaika_analiza_' 

# Układ współrzędnych (EPSG)
CRS_EPSG_CODE = 'epsg:2180'
CRS_EPSG = 'EPSG:2180' 

# Nazwy providerów i szablony URI
PROVIDER_MEMORY = 'memory'
URI_TEMPLATE_MEMORY = '{geometry_type}?crs={crs}'
URI_TEMPLATE_LINE = URI_TEMPLATE_MEMORY.format(geometry_type='LineString', crs=CRS_EPSG_CODE)
URI_TEMPLATE_POLYGON = URI_TEMPLATE_MEMORY.format(geometry_type='Polygon', crs=CRS_EPSG_CODE)


# =============================================================================
# Zmienne konfiguracyjne wejściowe
# =============================================================================

# Słownik warstw wejściowych (nazwy plików i wewnętrzne nazwy warstw)
INPUT_LAYERS = {
    'powiaty': {'filename': 'pow_pol.shp', 'layer_name': 'pow_pol'},
    'wydzielenia': {'filename': 'wydz_pol.shp', 'layer_name': 'wydz_pol'},
    'drogi_lesne': {'filename': 'kom_lin.shp', 'layer_name': 'kom_lin'},
    'oddzialy': {'filename': 'oddz_pol.shp', 'layer_name': 'oddz_pol'},
    'wydzielenia_opisy': {'filename': 'ow_pkt.shp', 'layer_name': 'ow_pkt'},
    'nadlesnictwo': {'filename': 'nadl_pol.shp', 'layer_name': 'nadl'},
}

# Słownik branż wykorzystywany w formularzach
INDUSTRIES = {
    "999": "Nie wybrano",
    "e": "Energetyka/OZE",
    "u": "Urząd",
    "td": "Transport/Drogi",
    "pg": "Planowanie/Geodezja",
    "wk": "WodKan",
    "s": "Środowisko",
    "rl": "Rolnictwo/Leśnictwo",
    "tk": "Telkom",
    "edu": "Edukacja",
    "i": "Inne",
    "it": "IT",
    "n": "Nieruchomości"
}

# Szablon URL serwisu WMTS oraz parametry mapy bazowej
WMTS_URL_TEMPLATE = (
    "contextualWMSLegend=0&crs={crs}&dpiMode=0&"
    "featureCount=10&format=image/jpeg&layers={layers}&"
    "styles=default&tileMatrixSet={crs}&url={url}"
)
MAPA_BAZOWA_LAYER_NAME = "Rastrowa Mapa Topograficzna Polski"
MAPA_BAZOWA_URL = 'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/TOPO?service%3DWMTS%26request%3DgetCapabilities'
MAPA_BAZOWA_LAYERS = "MAPA TOPOGRAFICZNA"

# Adresy i szablony URL do pobierania danych BDOT10k
BDOT10K_SHP_URL_TEMPLATE = 'https://opendata.geoportal.gov.pl/bdot10k/SHP/{}/{}_SHP.zip'

# Rozszerzenia i nazwy plików w archiwum BDOT10k
BDOT_FILE_SUFFIX_DROGI = 'SKDR_L.shp'
BDOT_FILE_SUFFIX_LINIE = 'SULN_L.shp'

# Nazwy warstw tymczasowych i pomocniczych w analizie
LAYER_NAME_WYDZIELENIA_PO_ANALIZIE = 'wydzielenia_po_analizie'
LAYER_NAME_BDOT10K_LINIE = 'linie_bdot10k'
LAYER_NAME_BDOT10K_DROGI = 'drogi_bdot10k'
LAYER_NAME_DROGI_LESNE_FILTER = "DROGI L"


# =============================================================================
# Zmienne konfiguracyjne logiki analizy
# =============================================================================

# Próg powierzchni obszarów w hektarach
AREA_HA_THRESHOLD = 1.5

# Klasy bonitacyjne gleby uwzględniane w analizie (do filtrowania)
SOIL_ROLES = ['RV', 'RIV']

# Słownik typów napięcia linii energetycznych
VOLTAGE_TYPES = {
    'najwyzszeNapiecie': 'najwyższego napięcia',
    'wysokieNapiecie': 'wysokiego napięcia',
    'srednieNapiecie': 'średniego napięcia',
    'niskieNapiecie': 'niskiego napięcia'
}

# Nazwy atrybutów oryginalnych (wejściowych)
ATTR_GL = 'g_l'
ATTR_KOD = 'kod_ob'
ATTR_ID_ADRES = 'id_adres'
ATTR_KATZARZ_ORIGINAL = 'KATZARZ'
ATTR_RODZAJ_ORIGINAL = 'RODZAJ'
ROAD_TYPE_FOREST = 'leśna'


# =============================================================================
# Zmienne konfiguracyjne warstw wynikowych
# =============================================================================

# Klucze warstw wynikowych 
LAYER_KEY_OBSZARY = 'obszary'
LAYER_KEY_LINIE = 'linie'
LAYER_KEY_DROGI = 'drogi'

# Nazwy atrybutów w warstwach wynikowych
ATTR_NR_OB = "nr_ob"
ATTR_ADR_LES = "adr_les"
ATTR_POW = "pow"
ATTR_ODL = "odl"
ATTR_RODZAJ = "rodzaj"

# Klucze słowników wewnętrznych (używane w przetwarzaniu danych)
RESULT_KEY_GEOMETRY = 'geometry'
RESULT_KEY_AREA_HA = 'area_ha'
RESULT_KEY_ID = 'id'
RESULT_KEY_NR_OB = 'nr_ob'
RESULT_KEY_DIST = 'dist'
RESULT_KEY_RODZAJ = 'rodzaj'

# Definicje warstw wynikowych
OUTPUT_LAYERS = {
    LAYER_KEY_OBSZARY: {
        'name': 'Wyznaczone obszary',
        'attributes': [ATTR_NR_OB, ATTR_ADR_LES, ATTR_POW]
    },
    LAYER_KEY_LINIE: {
        'name': 'Najbliższe linie energetyczne',
        'attributes': [ATTR_NR_OB, ATTR_ODL, ATTR_RODZAJ]
    },
    LAYER_KEY_DROGI: {
        'name': 'Najbliższe drogi',
        'attributes': [ATTR_NR_OB, ATTR_ODL, ATTR_RODZAJ]
    }
}


# =============================================================================
# Zmienne styli i wizualizacji
# =============================================================================

# Ustawienia etykietowania
LABEL_SETTINGS = {
    'font_family': "Arial",
    'font_size': 10,
    'color_rgb': '255, 153, 51',
    'buffer_size': 0.1,
    'x_offset': 2.0,
    'y_offset': 3.0
}

# Style dla warstw
LAYER_STYLES = {
    
    # Pobrane warstwy BDOT
    LAYER_NAME_BDOT10K_DROGI: {
        'line_color': 'gray', 
        'line_width': '0.26'
    },
    LAYER_NAME_BDOT10K_LINIE: {
        'line_color': 'red', 
        'line_width': '0.26'
    },

    # Warstwy analityczne (wynikowe) - linie
    OUTPUT_LAYERS[LAYER_KEY_LINIE]['name']: {
        'line_color': 'red', 
        'line_width': '0.5'
    },
    OUTPUT_LAYERS[LAYER_KEY_DROGI]['name']: {
        'line_color': 'gray', 
        'line_width': '0.5'
    },
    
    # Warstwy podstawowe (wejściowe) - linie
    INPUT_LAYERS['drogi_lesne']['layer_name']: {
        'line_color': 'gray', 
        'line_width': '0.26'
    },

    # Warstwy analityczne (wynikowe) - poligony
    OUTPUT_LAYERS[LAYER_KEY_OBSZARY]['name']: {
        'color': '#005023',
        'style': 'solid',
        'outline_color': 'black',
        'outline_style': 'solid',
        'outline_width': '0.26'
    },
    INPUT_LAYERS['wydzielenia']['layer_name']: {
        'color': '#005023',
        'style': 'solid',
        'outline_width': '0.26',
        'outline_color': 'black',
        'outline_style': 'solid'
    },
}

# =============================================================================
# Zmienne do raportu i layoutu
# =============================================================================

# Konfiguracja tabeli raportu (Excel)
EXCEL_REPORT_COLUMNS = [
    {'header': 'NR OBSZARU'},
    {'header': 'ADRES/Y LEŚNY/E'},
    {'header': 'POWIERZCHNIA OBSZARU (HA)'},
    {'header': 'ODLEGŁOŚĆ OD DROGI (M)'},
    {'header': 'RODZAJ DROGI'},
    {'header': 'ODLEGŁOŚĆ OD LINII ENERGETYCZNEJ (M)'},
    {'header': 'RODZAJ LINII ENERGETYCZNEJ'},
]
EXCEL_TABLE_STYLE = 'Table Style Medium 4'

# Konfiguracja wydruku (Map Layout)
LAYOUT_CONFIG = {
    'MARGINS': 20,
    'MAP': {
        'RECT': (20, 20, 20, 20),
        'POS_X': 20, 'POS_Y': 45,
        'SIZE_W': 190, 'SIZE_H': 126,
        'EXTENT_SCALE': 1.6
    },
    'LOGO_LP': {
        'PATH': ':/plugins/photovoltaics_LP/icons/logoLP.png',
        'ORIG_W': 300, 'ORIG_H': 300,
        'SCALE': 0.6,
        'POS_X': 20, 'POS_Y': 10
    },
    'LOGO_ENV': {
        'PATH': ':/plugins/photovoltaics_LP/icons/logoPL.png',
        'ORIG_W': 1588, 'ORIG_H': 401,
        'SCALE': 0.4,
        'POS_X': 215, 'POS_Y': 10
    },
    'ARROW': {
        'PATH': ':/plugins/photovoltaics_LP/icons/arrow.png',
        'ORIG_W': 949, 'ORIG_H': 893,
        'SCALE': 0.6,
        'POS_X': 225, 'POS_Y': 45
    },
    'TITLE': {
        'TEXT_TEMPLATE': "Obszary wyznaczone na potrzeby farm fotowoltaicznych - Nadleśnictwo {}",
        'FONT_SIZE': 13,
        'POS_X': 40, 'POS_Y': 15,
        'SIZE_W': 190, 'SIZE_H': 10
    },
    'FOOTER': {
        'TEXT': "Wygenerowano przy użyciu wtyczki Fotowoltaika LP",
        'FONT_SIZE': 11,
        'POS_X': 100, 'POS_Y': 190
    },
    'LEGEND': {
        'POS_X': 215, 'POS_Y': 107
    },
    'SCALEBAR': {
        'POS_X': 215, 'POS_Y': 161,
        'MAX_WIDTH': 70,
        'SEGMENTS': 5,
        'UNIT_LABEL': "km"
    }
}
