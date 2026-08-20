import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Aggiunta dinamica della cartella app al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent / "app"))

from main import app

client = TestClient(app)

def test_predict_success():
    """Verifica una richiesta valida con codice di stato 200 e struttura JSON corretta."""
    response = client.post("/predict", json={"review": "This product is amazing!"})
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)

def test_predict_method_not_allowed():
    """Verifica la risposta 405 inviando una richiesta GET a un endpoint che accetta solo POST."""
    response = client.get("/predict")
    assert response.status_code == 405

def test_predict_empty_payload():
    """Verifica l'errore di validazione 422 inviando un payload vuoto."""
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_predict_invalid_key():
    """Verifica l'errore di validazione 422 inviando una chiave JSON errata."""
    response = client.post("/predict", json={"text": "Wrong JSON key name"})
    assert response.status_code == 422

def test_route_not_found():
    """Verifica l'errore 404 richiedendo un endpoint inesistente."""
    response = client.get("/unexisting_endpoint")
    assert response.status_code == 404

def test_metrics_endpoint():
    """Verifica l'accessibilità dell'endpoint /metrics e la presenza delle metriche custom."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "sentiment_predictions_total" in response.text