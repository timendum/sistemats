# pylint: disable=C0111
from datetime import datetime

from openpyxl import load_workbook


class Excel:
    def __init__(self, filename):
        self._filename = filename
        self.workbook = load_workbook(filename=filename, data_only=True)
        self._current_row = None
        self._indexes = None
        self.__init_row()

    def __init_row(self):
        excel_mapping = {
            "emissione": "DATA",
            "documento": "N FATTURA",
            "pagamento": "DATA PAGAMENTO",
            "codice_fiscale": "C.F.",
            "importo": "NETTO PAGARE",
            "protocollo": "PROTOCOLLO",
            "pagamentoTracciato": "TRACCIATO",
            "opposizione": "OPPOSIZIONE",
            "bollo": "N. MARCA",
        }
        sheet = self.workbook.get_sheet_by_name("Fatture")
        index_row = sheet["1:1"]
        indexes = {}
        for cell in index_row:
            for key, value in excel_mapping.items():
                if not cell.value:
                    break
                if cell.value.strip() == value:
                    indexes[key] = cell.column_letter
                    break
        if len(indexes.keys()) != len(excel_mapping.keys()):
            raise ValueError("Non ho trovato tutte le intestazioni")
        self._indexes = indexes
        self._current_row = sheet["1:1"]

    def nuova_riga(self):
        excel_type = {
            "emissione": datetime,
            "documento": str,
            "pagamento": datetime,
            "codice_fiscale": str,
            "importo": (float, int),
            "pagamentoTracciato": str,
            "opposizione": (str, type(None)),
            "protocollo": (str, type(None)),
            "bollo": (str, type(None)),
        }
        current_row = self._current_row[0].row
        next_row = 1 + int(current_row)
        self._current_row = self._current_row[0].parent["%d:%d" % (next_row, next_row)]
        if not self._current_row[0].value:
            return None
        mapped = {}
        for cell in self._current_row:
            for key, value in self._indexes.items():
                if cell.column_letter == value:
                    if not isinstance(cell.value, excel_type[key]):
                        if cell.value is None:
                            raise ValueError(
                                "Errore nella cella %s: %s non compilato" % (cell.coordinate, key)
                            )
                        raise ValueError(
                            "Errore nella cella %s, %s non valido" % (cell.coordinate, key)
                        )
                    mapped[key] = cell.value
                    if isinstance(cell.value, str):
                        mapped[key] = mapped[key].strip()
                    break
        return mapped

    def protocollo(self, text):
        current_row = self._current_row[0].row
        cell = self._current_row[0].parent["%s%s" % (self._indexes["protocollo"], current_row)]
        cell.value = text

    def configurazione(self):
        excel_mapping = {
            "codice_fiscale": "codiceFiscale",
            "password": "password",
            "partita_iva": "partitaIva",
            "pincode": "pincode",
            "naturaPrestazione": "naturaPrestazione",
            "naturaBollo": "naturaBollo",
            "tipoSpesa": "tipoSpesa",
        }
        sheet = self.workbook.get_sheet_by_name("Sistema TS")
        mapped = {}
        for row in sheet.rows:
            for key, value in excel_mapping.items():
                if row[0].value == value:
                    if not isinstance(row[1], str):
                        mapped[key] = str(row[1].value)
                    else:
                        mapped[key] = row[1].value.strip()
                    break
        return mapped

    def save(self):
        self.workbook.save(self._filename)


def check_file(filename) -> bool:
    try:
        with open(filename, "ba") as _:
            pass
    except PermissionError:
        print("Chiudi Excel!")
        return False
    return True


if __name__ == "__main__":

    def main():
        import sys

        filename = "dati.xlsx"
        if sys.argv > 0:
            filename = sys.argv[1]
        excel = Excel(filename)
        print(excel.configurazione())
        while True:
            riga = excel.nuova_riga()
            if not riga:
                break
            print(riga)
            excel.protocollo("B")
        excel.save()

    main()
