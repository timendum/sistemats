# SistemaTS
Inserimento spese sanitarie 730 - Prestazione sanitarie

Gli script presenti in questo repository
permettono di inserire sul `sistemats`
dell’Agenzia delle entrate
le informazioni concernenti
le spese sanitarie
sostenute dai cittadini
, ai fini della precompilazione della dichiarazione dei redditi precompilata 730.

## Istruzioni

1. Installare i requisiti tramite `pip`

  ```pip install -r requirements.txt```

2. Copiare `dati_template.xlsx` su `dati.xlsx`

3. Inserire sul file Excel i propri dati nella tab _Dati personali_  
    È importante che il file rimanga in formato "2007".

4. Inserire nella tab _Spese_ tutte le informazioni necessarie

5. Se si vuole inviare il produzione, impostare la variabile di ambiente `TSPROD`.

6. Avviare `python main.py`

### Nota

Il programma elabora solo le righe
la cui colonna _protocollo_ è vuota
, saltando quindi le righe in cui l'invio è già stato effetuato.

## Tipologia di spesa

Il programma invia il codice "tipo spesa" = SP (Prestazioni Sanitarie).

È possibile
, nell'attuale implementazione,
inviare un solo tipo spesa alla volta.

Il suo valore è specificato nel file `webservices.py`.

## Informazioni e limitiazioni

Il seguento progetto è fornito secondo la **licenza Affero**,
'as-is',
senza nessuna garanzia sul suo funzionamento.

È stato sviluppato su Python 3.5,
probabilmente basta una qualsiasi versione 3.x
ma non viene verificato.

Suggerisco caldamente di installare il tutto tramite [virtualenv](https://virtualenv.pypa.io/).

Per maggiori informazioni fare riferimento al
[sito ufficiale](http://sistemats1.sanita.finanze.it/wps/portal/portalets/sistematsinforma/730%20-%20Spese%20sanitarie).
