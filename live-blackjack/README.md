# Live Blackjack

Blackjack a tutti gli effetti: il giocatore entra al tavolo, pesca carte,
si ferma o chiede altre carte, il banco gioca e il punteggio viene aggiornato
e salvato nel database.

## Struttura del progetto

```
live-blackjack/
├── app.py              # creazione dell'app, configurazione e migrazioni
├── blueprints/         # route della pagina (join, hit, stand, leave)
├── models/             # tabelle del database (Player, Game)
├── modules/            # logica di gioco: cards.py (carte), game.py (ciclo)
├── static/css/         # foglio di stile
├── templates/          # pagina del tavolo
├── migrations/         # migrazioni del database (Flask-Migrate)
├── tests/              # test di route, permessi e interfaccia
├── .env-example        # modello delle variabili d'ambiente
└── requirements.txt    # dipendenze del progetto
```

## Installazione

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Variabili d'ambiente (`.env`)

Il file `.env` contiene i valori che cambiano da una macchina all'altra e
non va mai committato. Per crearlo:

```bash
copy .env-example .env
```

| Variabile | Descrizione | Default |
|---|---|---|
| `SECRET_KEY` | chiave per firmare i cookie di sessione, obbligatoria in produzione | `blackjack-super-segreto` |
| `SQLALCHEMY_DATABASE_URI` | stringa di connessione al database | `sqlite:///blackjack.db` |

## Database e migrazioni

Lo schema è gestito da Flask-Migrate: `app.py` non crea più le tabelle da solo.

```bash
flask --app app db upgrade      # crea o aggiorna le tabelle
flask --app app db migrate -m "descrizione"   # dopo aver cambiato i modelli
```

Il file SQLite (`instance/blackjack.db`) viene ignorato da git.

## Avvio

```bash
python app.py
# oppure
flask --app app run
```

Poi apri `http://127.0.0.1:5000/`.

## Test

```bash
pytest
```

I test coprono le route (join, gioco, uscita), l'isolamento tra giocatori e
l'interfaccia. Usano un database in memoria, quindi non toccano i dati reali.

## Utenti e permessi

- Ogni giocatore ha una riga nel database, identificato dall'id salvato nella
  sessione del browser: non serve password, basta il nome.
- Tutte le route leggono il giocatore dalla sessione e agiscono solo sulle sue
  mani: un giocatore non può mai vedere o modificare le mani di un altro.
- Uscire dal tavolo chiude soltanto la sessione: scheda, punteggio e storico
  restano salvati, e rientrando con lo stesso nome si riprende tutto.
