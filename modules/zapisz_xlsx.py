from os import path
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtCore import QSettings, QFileInfo


class ZapiszXLSX:
    """Klasa zapisująca plik .xlsx.
    """

    def zapisz_xlsx(self) -> str:
        """Zapisuje plik .xlsx w wybranej lokalizacji.

        Returns:
            str:  wybrana ścieżka zapisu.
        """
        sciezka = QSettings().value("/excelSavePath", ".", type=str)
        (nazwa_pliku, filter) = QFileDialog.getSaveFileName(None,
                                                          "Zapisz jako plik excel...",
                                                          sciezka,
                                                          filter="Excel files (*.xlsx)",
                                                          )
        
        fn, rozszerzenie = path.splitext(nazwa_pliku)
        if len(fn) == 0:
            return
        QSettings().setValue("/excelSavePath", QFileInfo(nazwa_pliku).absolutePath())
        if rozszerzenie != '.xlsx':
            nazwa_pliku = nazwa_pliku + '.xlsx'
        return nazwa_pliku
