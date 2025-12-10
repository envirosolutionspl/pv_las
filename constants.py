# Adres URL kanału informacyjnego QGIS
FEED_URL = 'https://qgisfeed.envirosolutions.pl/'

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

# Układ współrzędnych (EPSG)
CRS_EPSG_2180 = 'EPSG:2180'

# Szablon URL serwisu WMTS oraz parametry mapy bazowej
WMTS_URL_TEMPLATE = (
    "contextualWMSLegend=0&crs={crs}&dpiMode=0&"
    "featureCount=10&format=image/jpeg&layers={layers}&"
    "styles=default&tileMatrixSet={crs}&url={url}"
)
MAPA_BAZOWA_LAYER_NAME = "Rastrowa Mapa Topograficzna Polski"
MAPA_BAZOWA_URL = 'https://mapy.geoportal.gov.pl/wss/service/WMTS/guest/wmts/TOPO?service%3DWMTS%26request%3DgetCapabilities'
MAPA_BAZOWA_LAYERS = "MAPA TOPOGRAFICZNA"

# Nazwy plików wejściowych oczekiwanych w archiwum ZIP
FILENAME_POWIATY = 'pow_pol.shp'
FILENAME_WYDZIELENIA = 'wydz_pol.shp'
FILENAME_DROGI_LESNE = 'kom_lin.shp'
FILENAME_ODDZIALY = 'oddz_pol.shp'
FILENAME_WYDZIELENIA_OPISY = 'ow_pkt.shp'
FILENAME_NADLESNICTWO = 'nadl_pol.shp'

# Wewnętrzne nazwy warstw używane w pluginie
LAYER_NAME_ODDZIALY = "oddz_pol"
LAYER_NAME_POWIATY = "pow_pol"
LAYER_NAME_WYDZIELENIA = "wydz_pol"
LAYER_NAME_DROGI_LESNE = "kom_lin"
LAYER_NAME_WYDZIELENIA_OPISY = "ow_pkt"
LAYER_NAME_NADLESNICTWO = "nadl"

# Nazwy warstw wynikowych generowanych przez analizę
RESULT_LAYER_OBSZARY = 'Wyznaczone obszary'
RESULT_LAYER_LINIE = 'Najbliższe linie energetyczne'
RESULT_LAYER_DROGI = 'Najbliższe drogi'

# Definicje stylów (kolory, grubości linii) dla warstw podstawowych
STYLE_COLOR_DROGI_LESNE = 'gray'
STYLE_WIDTH_DROGI_LESNE = '0.26'
STYLE_COLOR_WYDZIELENIA = '#005023'
STYLE_COLOR_WYDZIELENIA_OUTLINE = 'black'
STYLE_WIDTH_WYDZIELENIA = '0.26'


# Słownik typów napięcia linii energetycznych
VOLTAGE_TYPES = {
    'najwyzszeNapiecie':'najwyższego napięcia',
    'wysokieNapiecie': 'wysokiego napięcia' ,
    'srednieNapiecie': 'średniego napięcia',
    'niskieNapiecie': 'niskiego napięcia'
}

# Atrybuty dla analizy
ATTR_GL = 'g_l'
ATTR_ID_ADRES = 'id_adres'

# Klasy bonitacyjne gleby uwzględniane w analizie (do filtrowania)
SOIL_ROLES = {'RV', 'RIV'}

# Nazwy warstw tymczasowych i pomocniczych w analizie
LAYER_NAME_WYDZIELENIA_PO_ANALIZIE = 'wydzielenia_po_analizie'
LAYER_NAME_BDOT10K_LINIE = 'linie_bdot10k'
LAYER_NAME_BDOT10K_DROGI = 'drogi_bdot10k'
LAYER_NAME_DROGI_LESNE_FILTER = "DROGI L"

# Definicje stylów dla warstw analitycznych
STYLE_COLOR_LINIE_ENERGETYCZNE = 'red'
STYLE_WIDTH_LINIE_ENERGETYCZNE = '0.5'
STYLE_COLOR_DROGI = 'gray'
STYLE_WIDTH_DROGI = '0.5'

# Ustawienia etykietowania (czcionka, rozmiar, kolor)
LABEL_FONT_FAMILY = "Arial"
LABEL_FONT_SIZE = 10
LABEL_COLOR_RGB = '255, 153, 51'

# Nazwy atrybutów w warstwach wynikowych
ATTR_NR_OB = "nr_ob"
ATTR_ADR_LES = "adr_les"
ATTR_POW = "pow"
ATTR_ODL = "odl"
ATTR_RODZAJ = "rodzaj"

# Adresy i szablony URL do pobierania danych BDOT10k
BDOT10K_SHP_URL_TEMPLATE = 'https://opendata.geoportal.gov.pl/bdot10k/SHP/{}/{}_SHP.zip'

# Rozszerzenia i nazwy plików w archiwum BDOT10k
BDOT_FILE_SUFFIX_DROGI = 'SKDR_L.shp'
BDOT_FILE_SUFFIX_LINIE = 'SULN_L.shp'

# Style dla pobranych warstw BDOT
STYLE_COLOR_BDOT_DROGI = 'gray'
STYLE_WIDTH_BDOT_DROGI = '0.26'
STYLE_COLOR_BDOT_LINIE = 'red'
STYLE_WIDTH_BDOT_LINIE = '0.26'

# Konfiguracja wydruku (Layout)
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
