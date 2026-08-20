import asyncio
import logging
import pickle
import time
import psutil
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configurazione Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("sentiment_api")

# Metriche Custom per Prometheus
PREDICT_COUNTER = Counter("sentiment_predictions_total", "Totale predizioni eseguite", ["sentiment"])
PREDICT_LATENCY = Histogram("sentiment_prediction_latency_seconds", "Latenza di elaborazione predizioni in secondi")
ERROR_COUNTER = Counter("sentiment_prediction_errors_total", "Totale errori di sistema/predizione")
CPU_GAUGE = Gauge("process_cpu_usage_percent", "Percentuale di CPU utilizzata dal processo")
RAM_GAUGE = Gauge("process_memory_bytes", "Utilizzo memoria RAM in Bytes")

# INIZIALIZZAZIONE METRICA ERRORI: Espone la metrica a 0 fin dal primo secondo
ERROR_COUNTER.inc(0)

async def monitor_resources():
    """Monitora continuamente CPU e RAM aggiornando le metriche Prometheus."""
    psutil.cpu_percent(interval=None)  # Inizializzazione punto di riferimento CPU
    while True:
        try:
            # Calcolo CPU globale e RAM occupata dal processo Python
            cpu_val = psutil.cpu_percent(interval=None)
            ram_val = psutil.Process().memory_info().rss

            CPU_GAUGE.set(cpu_val)
            RAM_GAUGE.set(ram_val)
        except Exception as e:
            logger.error(f"Errore lettura metriche risorse: {e}")

        await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitor_resources())
    logger.info("Task di monitoraggio risorse avviato in background.")
    yield
    task.cancel()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(monitor_resources())
    logger.info("Task di monitoraggio risorse avviato in background.")
    yield
    task.cancel()
# Uso del path relativo per garantire la portabilità
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "sentiment_analysis_model.pkl"

app = FastAPI(
    title="Sentiment Analysis DevOps API",
    description="API REST per la classificazione del sentiment di recensioni e monitoraggio delle prestazioni in tempo reale.",
    version="1.0.0",
    lifespan=lifespan
)

# Caricamento del modello ML
try:
    logger.info(f"Tentativo di caricamento modello da: {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("Modello caricato con successo.")
except Exception as e:
    logger.critical(f"Errore critico nel caricamento del file model.pkl: {e}", exc_info=True)
    raise RuntimeError(f"Errore critico nel caricamento del file model.pkl: {e}")

class ReviewRequest(BaseModel):
    review: str = Field(
        ...,
        description="Testo della recensione in lingua inglese da analizzare",
        example="This product is amazing! Highly recommended."
    )

class ReviewResponse(BaseModel):
    sentiment: str = Field(
        ...,
        description="Etichetta del sentimento stimata dal modello ML",
        example="positive"
    )
    confidence: float = Field(
        ...,
        description="Punteggio di probabilità della prediction (da 0.0 a 1.0)",
        example=0.95
    )

@app.post(
    "/predict",
    response_model=ReviewResponse,
    summary="Analisi del Sentiment",
    description="Riceve una recensione testuale ed esegue la predizione del sentiment tramite il modello di Machine Learning.",
    response_description="Restituisce il sentiment identificato (es. positive, negative).",
    status_code=status.HTTP_200_OK
)
def predict(data: ReviewRequest):
    start_time = time.time()
    logger.info(f"Ricevuta richiesta di prediction. Lunghezza testo: {len(data.review)} caratteri.")
    try:
        prediction = model.predict([data.review])[0]
        # Estrazione della probabilità/confidenza se supportata dal modello
        confidence = 1.0
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([data.review])[0]
            confidence = float(max(probabilities))
        elapsed = time.time() - start_time

        # Aggiornamento delle metriche Prometheus
        PREDICT_COUNTER.labels(sentiment=str(prediction)).inc()
        PREDICT_LATENCY.observe(elapsed)

        logger.info(f"Predizione completata in {elapsed:.4f}s. Esito: {prediction} (probabilità: {confidence:.2f})")

        return ReviewResponse(
            sentiment=str(prediction),
            confidence=round(confidence, 4)
        )
    except Exception as e:
        ERROR_COUNTER.inc()
        logger.error(f"Errore durante l'elaborazione della predizione: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore interno durante l'elaborazione della prediction: {str(e)}"
        )

@app.get(
    "/metrics",
    summary="Endpoint Metriche Prometheus",
    description="Espone le metriche applicative e di sistema per lo scrape periodico di Prometheus.",
    response_description="Metriche in formato testo standard Prometheus."
)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)