# pylint: disable=C0111
from datetime import datetime
from openpyxl import load_workbook

class Excel():
    def __init__(self, filename):
        self._filename = filename
        self.workbook = load_workbook(filename=filename, data_only=True)
        self._current_row = None
        self._indexes = None
        self.__init_row()

    def __init_row(self):
        excel_mapping = {
            'emissione': 'dataEmissione',
            'documento': 'numDocumento',
            'pagamento': 'dataPagamento',
            'codice_fiscale': 'codiceFiscaleCliente',
            'importo': 'importo',
            'protocollo': 'protocollo'
        }
        sheet = self.workbook.get_sheet_by_name('Spese')
        index_row = sheet['1:1']
        indexes = {}
        for cell in index_row:
            for key, value in excel_mapping.items():
                if cell.value == value:
                    indexes[key] = cell.column
                    break
        if len(indexes.keys()) != len(excel_mapping.keys()):
            raise ValueError('Non ho trovato tutte le intestazioni')
        self._indexes = indexes
        self._current_row = sheet['1:1']

    def nuova_riga(self):
        excel_type = {
            'emissione': datetime,
            'documento': str,
            'pagamento': datetime,
            'codice_fiscale': str,
            'importo': float,
            'protocollo': (str, type(None))
        }
        current_row = self._current_row[0].row
        next_row = 1 + int(current_row)
        self._current_row = self._current_row[0].parent['%d:%d' % (next_row, next_row)]
        if not self._current_row[0].value:
            return None
        mapped = {}
        for cell in self._current_row:
            for key, value in self._indexes.items():
                if cell.column == value:
                    if not isinstance(cell.value, excel_type[key]):
                        raise ValueError(
                            'Errore di tipo nella cella %s (%s vs %s)' %
                            (cell.coordinate, type(cell.value), excel_type[key])
                        )
                    mapped[key] = cell.value
                    break
        return mapped

    def protocollo(self, text):
        current_row = self._current_row[0].row
        cell = self._current_row[0].parent['%s%s' % (self._indexes['protocollo'], current_row)]
        cell.value = text

    def configurazione(self):
        excel_mapping = {
            'codice_fiscale': 'codiceFiscale',
            'password': 'password',
            'partita_iva': 'partitaIva',
            'pincode': 'pincode'

        }
        sheet = self.workbook.get_sheet_by_name('Dati personali')
        mapped = {}
        for row in sheet.rows:
            for key, value in excel_mapping.items():
                if row[0].value == value:
                    mapped[key] = row[1].value
                    break
        return mapped

    def save(self):
        self.workbook.save(self._filename)


if __name__ == "__main__":
    def main():
        excel = Excel('dati.xlsx')
        print(excel.configurazione())
        while True:
            riga = excel.nuova_riga()
            if not riga:
                break
            print(riga)
            excel.protocollo('B')
        excel.save()

    main()
