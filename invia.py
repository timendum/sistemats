# pylint: disable=C0111
from decimal import Decimal
import sys

from excel import Excel
from openssl import OpenSSL
from webservices import send_data


IMPORTO_BOLLO = 2


def moneyfmt(value, places=2, curr="", sep=",", dp=".", pos="", neg="-", trailneg=""):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else "0")
    if places:
        build(dp)
    if not digits:
        build("0")
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return "".join(reversed(result))


def check_file(filename) -> bool:
    try:
        with open(filename, "ba") as _:
            pass
    except PermissionError:
        print("Chiudi Excel!")
        return False
    return True


if __name__ == "__main__":

    def mapping(configurazione, riga, openssl):
        mapped = {
            "username": configurazione["codice_fiscale"].strip(),
            "password": configurazione["password"].strip(),
            "pincode": openssl.encrypt(str(configurazione["pincode"]).strip()),
            "cfProprietario": openssl.encrypt(configurazione["codice_fiscale"].strip()),
            "pIva": str(configurazione["partita_iva"]).strip(),
            "dataEmissione": riga["emissione"].strftime("%Y-%m-%d"),
            "numDocumento": str(riga["documento"]).strip(),
            "dataPagamento": riga["pagamento"].strftime("%Y-%m-%d"),
            "cfCittadino": openssl.encrypt(riga["codice_fiscale"].strip()),
            "importo": moneyfmt(Decimal(riga["importo"]), sep=""),
            "naturaPrestazione": configurazione["naturaPrestazione"].strip(),
            "naturaBollo": configurazione["naturaBollo"].strip(),
            "pagamentoTracciato": riga["pagamentoTracciato"].strip().upper(),
            "flagOpposizione": "0",
            "tipoSpesa": configurazione["tipoSpesa"].strip(),
        }
        if mapped["dataPagamento"] < mapped["dataEmissione"]:
            mapped["flagPagamentoAnticipato"] = 1
        if riga["bollo"] and riga["bollo"].strip():
            mapped["importo"] = moneyfmt(Decimal(riga["importo"]) - IMPORTO_BOLLO, sep="")
            mapped["bollo"] = moneyfmt(Decimal(IMPORTO_BOLLO), sep="")
        if riga["opposizione"] and "si" == riga["opposizione"].lower():
            mapped["flagOpposizione"] = "1"
            del mapped["cfProprietario"]
        return mapped

    def main():
        filename = "fatture.xlsx"
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        if not check_file(filename):
            return
        excel = Excel(filename)
        openssl = OpenSSL("data/SanitelCF.cer")
        configurazione = excel.configurazione()
        try:
            while True:
                try:
                    riga = excel.nuova_riga()
                except ValueError as e:
                    print(e)
                    continue
                if not riga:
                    break
                if riga.get("protocollo"):
                    # riga con già il numero di protocollo
                    continue
                mapped = mapping(configurazione, riga, openssl)
                result = send_data(mapped)
                print("%s - %s" % (mapped["numDocumento"], result[1]))
                excel.protocollo(result[1])
        finally:
            excel.save()

    main()
