# pylint: disable=C0111
import os

import requests
import xmltodict

PROD = os.getenv('TSPROD', False)

if not PROD:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    ENDPOINT = \
        'https://invioSS730pTest.sanita.finanze.it/DocumentoSpesa730pWeb/DocumentoSpesa730pPort'
    VERIFY_SSL = False
    print('** Invio in TEST')
else:
    VERIFY_SSL = True
    ENDPOINT = \
        'https://invioSS730p.sanita.finanze.it/DocumentoSpesa730pWeb/DocumentoSpesa730pPort'
    print('*** Invio in PRODUZIONE! ***')

HEADERS = {'content-type': 'text/xml',
           'SOAPAction': '"inserimento.documentospesap730.sanita.finanze.it"'}

BASE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
 xmlns:doc="http://documentospesap730.sanita.finanze.it">
   <soapenv:Header/>
   <soapenv:Body>
      <doc:inserimentoDocumentoSpesaRequest>
         <doc:opzionale1></doc:opzionale1>
         <doc:opzionale2></doc:opzionale2>
         <doc:opzionale3></doc:opzionale3>
         <doc:pincode>{pincode}</doc:pincode>
         <doc:Proprietario>
            <doc:cfProprietario>{cfProprietario}</doc:cfProprietario>
         </doc:Proprietario>
         <doc:idInserimentoDocumentoFiscale>
            <doc:idSpesa>
               <doc:pIva>{pIva}</doc:pIva>
               <doc:dataEmissione>{dataEmissione}</doc:dataEmissione>
               <doc:numDocumentoFiscale>
                  <doc:dispositivo>1</doc:dispositivo>
                  <doc:numDocumento>{numDocumento}</doc:numDocumento>
               </doc:numDocumentoFiscale>
            </doc:idSpesa>
            <doc:dataPagamento>{dataPagamento}</doc:dataPagamento>
            <doc:cfCittadino>{cfCittadino}</doc:cfCittadino>
            <doc:voceSpesa>
               <doc:tipoSpesa>SP</doc:tipoSpesa>
               <doc:importo>{importo}</doc:importo>
            </doc:voceSpesa>
         </doc:idInserimentoDocumentoFiscale>
      </doc:inserimentoDocumentoSpesaRequest>
   </soapenv:Body>
</soapenv:Envelope>"""

S_PROTOCOLLO = 'http://documentospesap730.sanita.finanze.it:protocollo'
S_ENVELOPE = 'http://schemas.xmlsoap.org/soap/envelope/:Envelope'
S_BODY = 'http://schemas.xmlsoap.org/soap/envelope/:Body'
S_FAULT = 'http://schemas.xmlsoap.org/soap/envelope/:Fault'
S_DSF = 'http://documentospesap730.sanita.finanze.it'
S_RESPONSE = S_DSF +':inserimentoDocumentoSpesaResponse'
S_DESCRIZIONE = S_DSF + ':descrizione'
S_LISTAMESSAGGI = S_DSF + ':listaMessaggi'
S_MESSAGGIO = S_DSF + ':messaggio'

def send_data(data):
    body = BASE.format(**data)
    response = requests.post(ENDPOINT, data=body, headers=HEADERS, verify=VERIFY_SSL,
                             auth=(data['username'], data['password']))
    if response.status_code != 200:
        if response.status_code == 500:
            esito = None
            try:
                soap_response = xmltodict.parse(response.content, process_namespaces=True)
                esito = soap_response[S_ENVELOPE][S_BODY][S_FAULT]['faultstring']
            except KeyError:
                pass
            if esito:
                raise ValueError('Errore durante la richiesta: %s' % esito)
            else:
                raise ValueError('Errore durante la richiesta: %d' % response.status_code)
    soap_response = xmltodict.parse(response.content, process_namespaces=True)
    esito = soap_response[S_ENVELOPE][S_BODY][S_RESPONSE]
    if esito.get(S_PROTOCOLLO):
        return (True, esito[S_PROTOCOLLO])
    else:
        try:
            return (False, esito[S_LISTAMESSAGGI][S_MESSAGGIO][S_DESCRIZIONE])
        except TypeError:
            return (False, '; '.join([messaggio[S_DESCRIZIONE]
                                      for messaggio in esito[S_LISTAMESSAGGI][S_MESSAGGIO]])
                   )


if __name__ == "__main__":
    def main():
        data = {
            # pylint: disable=C0301
            'username': 'MTOMRA66A41G224M',
            'password': 'Salve123',
            'pincode': 'W+cy4Lz7rOOgldsbK98TEAwR6OIikKMkQJ1nWS09LgnJ6up+4e2LfIHe9z6aOQ9NocHOqepHuUcqmNNXpOq2JDCZQms65cX2oif8VhSUsvOk/9mc/8A9A7tpLnHcoGNrrjrg0z3fat7JmENXo5LF5uQV2IqvT4z5BDJbNa5XZpQ=',
            'cfProprietario': 'SsFrZY1plknIYKxk2MxIsgCyH2X3cfnrbg7B1aywMzw4SYwfzCa797Bb40vZMlS1pRjBki3SYZT/dao7W7SCwarTTLQqFmfXu7SGBStGzfAyVWcXAZapnW3d8QWfY7EgbktdHPfcoslCqY+K4JJrHQA9H2bk2ngSA7n+xOjuLVw=',
            'pIva': '65498732105',
            'dataEmissione': '2016-01-01',
            'numDocumento': 'P0012',
            'dataPagamento': '2016-01-01',
            'cfCittadino': 'iKvd9JQntqxPBT2UA/OFfztSNLidocP8Op+NfODzfTdxFWzkcdZrJz5gvCuqv7Dh/r3Cin1ZQMmg/BofIqYCyq2PcC+PJzbvQCocDdl6FrXVXs3W5JhnX7VpWFGCLPYYY2WL+RWKxhfkGqeY8+NCVfQ1lEA15g3W5AabJ15Tthk=',
            'importo': '25.3'
        }
        print(send_data(data))

    main()
