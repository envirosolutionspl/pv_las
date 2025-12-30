# =============================================================================
# Zmienne systemowe i globalne
# =============================================================================

# Adres URL kanału informacyjnego QGIS
FEED_URL = 'https://qgisfeed.envirosolutions.pl/'

# Katalog tymczasowy
TEMP_DIR_PREFIX = 'fotowoltaika_analiza_' 

# Układ współrzędnych (EPSG)
CRS_EPSG = '2180' 

# Szablony URI
URI_TEMPLATE_MEMORY = '{geometry_type}?crs=epsg:{crs}'
URI_TEMPLATE_LINE = URI_TEMPLATE_MEMORY.format(geometry_type='LineString', crs=CRS_EPSG)
URI_TEMPLATE_POLYGON = URI_TEMPLATE_MEMORY.format(geometry_type='Polygon', crs=CRS_EPSG)


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
    'nadlesnictwo': {'filename': 'nadl_pol.shp', 'layer_name': 'nadl_pol'},
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
INPUT_ATTRS = {
    'gl': 'g_l',
    'kod': 'kod_ob',
    'id_adres': 'id_adres',
    'katzarz': 'KATZARZ',
    'rodzaj': 'RODZAJ',
    'adr_les': 'adr_les'
}

# Typ drogi lesnej
ROAD_TYPE_FOREST = 'leśna'

# =============================================================================
# Zmienne konfiguracyjne warstw wynikowych
# =============================================================================

# Klucze warstw wynikowych 
LAYER_KEY_OBSZARY = 'obszary'
LAYER_KEY_LINIE = 'linie'
LAYER_KEY_DROGI = 'drogi'

# Nazwy atrybutów w warstwach wynikowych
OUTPUT_ATTRS = {
    'nr_ob': 'nr_ob',
    'adres_lesny': 'adr_les',
    'powierzchnia': 'pow',
    'odleglosc': 'odl',
    'rodzaj': 'rodzaj'   
}

# Klucze słowników wewnętrznych (używane w przetwarzaniu danych)
RESULT_KEYS = {
    'geometry': 'geometry',
    'area_ha': 'area_ha',
    'id': 'id',
    'nr_ob': 'nr_ob',
    'dist': 'dist',
    'rodzaj': 'rodzaj'
}

# Nazwy warstw wynikowych
NAME_LAYER_OBSZARY = 'Wyznaczone obszary'
NAME_LAYER_LINIE = 'Najbliższe linie energetyczne'
NAME_LAYER_DROGI = 'Najbliższe drogi'



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
    NAME_LAYER_LINIE: {
        'line_color': 'red', 
        'line_width': '0.5'
    },
    NAME_LAYER_DROGI: {
        'line_color': 'gray', 
        'line_width': '0.5'
    },
    
    # Warstwy podstawowe (wejściowe) - linie
    INPUT_LAYERS['drogi_lesne']['layer_name']: {
        'line_color': 'gray', 
        'line_width': '0.26'
    },

    # Warstwy analityczne (wynikowe) - poligony
    NAME_LAYER_OBSZARY: {
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
# Konfiguracja techniczna
# =============================================================================

ENCODINGS = {
    'UTF8': 'UTF-8',
    'WIN1250': 'windows-1250'
}

PROVIDERS = {
    'OGR': 'ogr',
    'WMS': 'wms',
    'MEMORY': 'memory'
}

FILE_FILTERS = {
    'ZIP': "Archiwum ZIP (*.zip)",
    'SHP': "*.shp",
    'EXCEL': "Excel files (*.xlsx)",
    'IMAGES': "jpg (*.jpg);;bitmap (*.bmp);;tiff (*.tiff);; pdf (*.pdf)"
}

DRIVER_SHAPEFILE = 'ESRI Shapefile'

# =============================================================================
# Domyślne nazwy plików i warstw (wynikowe)
# =============================================================================
FILENAME_DEFAULT_XLSX = "Raport"
FILENAME_DEFAULT_LAYERS_DIR = "wyznaczone_obszary"
FILENAME_LAYER_LINIE = 'najblizsze_linie_energetyczne.shp'
FILENAME_LAYER_DROGI = 'najblizsze_drogi.shp'


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
    'PAGE': {
        'SIZE_W': 297, 'SIZE_H': 210,
    },
    'MAP': {
        'RECT': (20, 20, 20, 20),
        'POS_X': 20, 'POS_Y': 45,
        'SIZE_W': 190, 'SIZE_H': 126,
        'EXTENT_SCALE': 1.6
    },
    'LOGO_LP': {
        'PATH': 'icons/logoLP.png',
        'ORIG_W': 300, 'ORIG_H': 300,
        'SCALE': 0.6,
        'POS_X': 20, 'POS_Y': 10
    },
    'LOGO_ENV': {
        'PATH': 'icons/logoPL.png',
        'ORIG_W': 1588, 'ORIG_H': 401,
        'SCALE': 0.4,
        'POS_X': 215, 'POS_Y': 10
    },
    'ARROW': {
        'PATH': 'icons/arrow.png',
        'ORIG_W': 949, 'ORIG_H': 893,
        'SCALE': 0.6,
        'POS_X': 225, 'POS_Y': 45
    },
    'TITLE': {
        'TEXT_TEMPLATE': "Obszary wyznaczone na potrzeby farm fotowoltaicznych - Nadleśnictwo {}",
        'ATTR_NAME': 'nzw_nadl',
        'FONT_TYPE': 'Arial',
        'FONT_SIZE': 13,
        'POS_X': 40, 'POS_Y': 15,
        'SIZE_W': 190, 'SIZE_H': 10
    },
    'FOOTER': {
        'TEXT': "Wygenerowano przy użyciu wtyczki Fotowoltaika LP",
        'FONT_TYPE': 'Arial',
        'FONT_SIZE': 11,
        'POS_X': 100, 'POS_Y': 190
    },
    'LEGEND': {
        'POS_X': 215, 'POS_Y': 107
    },
    'SCALEBAR': {
        'POS_X': 215, 'POS_Y': 161,
        'FONT_TYPE': 'Arial',
        'FONT_SIZE': 9,
        'MAX_WIDTH': 70,
        'SEGMENTS': 5,
        'UNITS_PER_SEGMENT': 3.0,
        'MAP_UNITS_PER_SCALE_BAR_UNIT': 1000.0,
        'UNIT_LABEL': "km"
    }
}
