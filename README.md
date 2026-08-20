# Sentiment Analysis DevOps Pipeline & Monitoring

Questo repository contiene la soluzione completa per l'automatizzazione del deploy, del testing e del monitoraggio in tempo reale di un servizio REST API per la Sentiment Analysis di recensioni in lingua inglese.

---
## 🏗 Architettura del Sistema

L'infrastruttura si compone dei seguenti moduli integrati tramite Docker Compose:

* **API REST (FastAPI & Scikit-Learn)**: Espone l'endpoint di predizione ML e calcola la probabilità. Espone inoltre le metriche applicative e di sistema.
* **CI/CD (Jenkins Pipeline)**: Automatizza unit test, deploy dei container, test di integrazione end-to-end e invio di notifiche di stato.
* **Monitoraggio (Prometheus & Grafana)**: Prometheus raccoglie periodicamente le metriche dall'API, mentre Grafana le visualizza tramite una dashboard pre-configurata via codice (*dashboard provisioning*).

---

## 📁 Struttura del Repository

```text
sentiment-devops/
├── app/
│   ├── main.py                    # Codice FastAPI + Metriche Prometheus + Background Task
│   ├── requirements.txt           # Dipendenze Python del progetto
│   └── sentiment_analysis_model.pkl # Modello ML serializzato
├── tests/
│   ├── test_unit.py               # Test unitari in memoria (Pytest)
│   └── test_integration.py        # Test di integrazione HTTP end-to-end
├── prometheus/
│   └── prometheus.yml             # Configurazione dello scrape periodico di Prometheus
├── grafana/
│   ├── dashboards/
│   │   └── sentiment_dashboard.json # Configurazione della Dashboard Grafana
│   └── provisioning/              # Auto-caricamento datasource e dashboard
│       ├── dashboards/dashboards.yml
│       └── datasources/datasource.yml
├── Dockerfile                     # Containerizzazione dell'API FastAPI
├── docker-compose.yml             # Orchestrazione dell'intero stack (API, Prometheus, Grafana)
├── Jenkinsfile                    # Pipeline CI/CD dichiarativa per Jenkins
└── README.md                      # Documentazione di progetto

```

---

## ⚙️ Configurazione e Avvio Rapido

### Prerequisiti

* **Docker Desktop** (attivo ed in esecuzione)
* **Git**

### Avvio dell'Infrastruttura

Per compilare ed avviare l'intero stack in background esegui:

```bash
docker compose up --build -d

```

Verifica lo stato dei container:

```bash
docker compose ps

```

---

## 🔌 API Endpoints

### 1. Analisi del Sentimento

* **URL**: `POST /predict`
* **Content-Type**: `application/json`

**Request Body**:

```json
{
  "review": "This product is amazing! I love it."
}

```

**Response Body (200 OK)**:

```json
{
  "sentiment": "positive",
  "confidence": 0.9852
}

```

### 2. Metriche Prometheus

* **URL**: `GET /metrics`
* **Response**: Formato testo conforme allo standard Prometheus avente metriche su tempo di risposta, errori di predizione, contatore richieste, utilizzo CPU e RAM.

---

## 📊 Dashboard di Monitoraggio (Grafana)

* **URL Grafana**: `http://localhost:3000` (Credenziali: `admin` / `admin`)
* **URL Prometheus**: `http://localhost:9090`

La dashboard **Sentiment Analysis Dashboard** viene caricata automaticamente all'avvio e include 5 pannelli in tempo reale:

1. **Tempo di risposta delle richieste**: Latenza media di calcolo della predizione.
2. **Errori di predizione**: Contatore cumulativo degli errori interni.
3. **Totale Predizioni**: Breakout per tipologia di sentimento (`positive`, `negative`, `neutral`).
4. **Utilizzo CPU %**: Percentuale di utilizzo della CPU aggiornata ogni 2 secondi in background.
5. **Utilizzo RAM**: Memoria fisica allocata espressa in Megabytes/Gigabytes.

---

## 🔄 Pipeline CI/CD (Jenkins)

Lo script `Jenkinsfile` definisce una pipeline a 4 fasi:

1. **Checkout**: Download del codice sorgente dal repository remoto.
2. **Unit Tests**: Creazione dell'ambiente virtuale ed esecuzione dei test isolati (`test_unit.py`).
3. **Build & Deploy Containers**: Ricostruzione e riavvio dei container tramite Docker Compose.
4. **Integration Tests**: Verifica HTTP end-to-end contro il container attivo (`test_integration.py`).
5. **Post Actions**: Notifica dell'esito della pipeline via log/email e pulizia del workspace.

---

## 🛠 Manutenzione e Troubleshooting

* **Visualizzare i log in tempo reale**:
```bash
docker compose logs -f api

```


* **Arresto dell'infrastruttura**:
```bash
docker compose down

```


* **Arresto con rimozione dei volumi**:
```bash
docker compose down -v

```


* **Esecuzione manuale dei test in locale**:
```bash
pytest -W ignore::DeprecationWarning

```