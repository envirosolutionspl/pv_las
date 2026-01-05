import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, 'data')

GPKG_ANALIZA = 'dane_wejsciowe_analiza.gpkg'
GPKG_EKSPORT = 'dane_wejsciowe_eksport.gpkg'
GPKG_POWIATY = 'pow_pol.gpkg'
ZIP_TEST_LAYERS = 'test_layers.zip'

# Bazowy adres URL do pobierania danych testowych
TEST_DATA_BASE_URL = 'https://downloads.envirosolutions.pl/dane/'

FILENAME_REPORT_XLSX = 'output_test_raport.xlsx'
FILENAME_WYDRUK_PDF = 'output_wydruk.pdf'
FILENAME_WYDRUK_JPG = 'output_wydruk.jpg'

DIR_SHP_TEMP = 'output_shp_temp'

EXPECTED_FEATURE_COUNT = 49
    
