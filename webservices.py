# pylint: disable=C0111
import os

from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from zeep import Client
from zeep.transports import Transport

PROD = os.getenv("TSPROD", False)

if not PROD:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    ENDPOINT = (
        "https://invioSS730pTest.sanita.finanze.it/DocumentoSpesa730pWeb/DocumentoSpesa730pPort"
    )
    VERIFY_SSL = False
    print("** Invio in TEST")
else:
    VERIFY_SSL = True
    ENDPOINT = "https://invioSS730p.sanita.finanze.it/DocumentoSpesa730pWeb/DocumentoSpesa730pPort"
    print("*** Invio in PRODUZIONE! ***")


def send_data(data):
    proprietario = {"cfProprietario": data["cfProprietario"]}
    documentoSpesa = {
        "idSpesa": {
            "pIva": data["pIva"],
            "dataEmissione": data["dataEmissione"],
            "numDocumentoFiscale": {"dispositivo": "1", "numDocumento": data["numDocumento"]},
        },
        "dataPagamento": data["dataPagamento"],
        "cfCittadino": data["cfCittadino"],
        "voceSpesa": {"tipoSpesa": "SP", "importo": data["importo"]},
        "pagamentoTracciato": data["pagamentoTracciato"],
    }
    session = Session()
    session.verify = VERIFY_SSL
    session.auth = HTTPBasicAuth(data["username"], data["password"])
    client = Client("data/DocumentoSpesa730p.wsdl", transport=Transport(session=session))
    service = client.create_service(
        "{http://documentospesap730.sanita.finanze.it}DocumentoSpesa730pServicePortBinding",
        ENDPOINT,
    )
    try:
        esito = service.Inserimento(
            pincode=data["pincode"],
            Proprietario=proprietario,
            idInserimentoDocumentoFiscale=documentoSpesa,
        )
    except RequestException as e:
        raise ValueError("Errore durante la richiesta: %s" % e)
    if esito["protocollo"]:
        return (True, esito["protocollo"])
    else:
        return (
            False,
            "; ".join(
                [messaggio["descrizione"] for messaggio in esito["listaMessaggi"]["messaggio"]]
            ),
        )


if __name__ == "__main__":
    import datetime
    import random

    def main():
        data = {
            "username": "MTOMRA66A41G224M",
            "password": "Salve123",
            "pincode": "W+cy4Lz7rOOgldsbK98TEAwR6OIikKMkQJ1nWS09LgnJ6up+4e2LfIHe9z6aOQ9NocHOqepHuUcqmNNXpOq2JDCZQms65cX2oif8VhSUsvOk/9mc/8A9A7tpLnHcoGNrrjrg0z3fat7JmENXo5LF5uQV2IqvT4z5BDJbNa5XZpQ=",
            "cfProprietario": "SsFrZY1plknIYKxk2MxIsgCyH2X3cfnrbg7B1aywMzw4SYwfzCa797Bb40vZMlS1pRjBki3SYZT/dao7W7SCwarTTLQqFmfXu7SGBStGzfAyVWcXAZapnW3d8QWfY7EgbktdHPfcoslCqY+K4JJrHQA9H2bk2ngSA7n+xOjuLVw=",
            "pIva": "65498732105",
            "dataEmissione": datetime.date.today(),
            "numDocumento": "P00{:d}".format(random.randint(1, 100)),
            "dataPagamento": datetime.date.today(),
            "cfCittadino": "iKvd9JQntqxPBT2UA/OFfztSNLidocP8Op+NfODzfTdxFWzkcdZrJz5gvCuqv7Dh/r3Cin1ZQMmg/BofIqYCyq2PcC+PJzbvQCocDdl6FrXVXs3W5JhnX7VpWFGCLPYYY2WL+RWKxhfkGqeY8+NCVfQ1lEA15g3W5AabJ15Tthk=",
            "importo": "25.3",
            "pagamentoTracciato": random.choice(["SI", "NO"]),
        }
        print(send_data(data))

    main()
