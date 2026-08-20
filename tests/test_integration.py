import os
import requests

# Prende l'URL dell'API dalle variabili d'ambeinte o usa localhost come fallback
API_URL = os.getenv("API_URL", "http://localhost:8000")


def test_integration_predict_end_to_end():
    """Testa l'endpoint /predict eseguendo una chiamata HTTP reale verso il container attivo."""
    url = f"{API_URL}/predict"
    payload = {"review": "The product works surprisingly well and fast."}

    response = requests.post(url, json=payload, timeout=5)

    assert response.status_code == 200, f"Atteso 200, ricevuto {response.status_code}"
    data = response.json()
    assert "sentiment" in data
    assert data["sentiment"] in ["positive", "negative", "neutral"]
    assert "confidence" in data


def test_integration_prometheus_metrics_exposed():
    """Testa se Prometheus riesce a leggere le metriche esposte dall'API in container."""
    url = f"{API_URL}/metrics"
    response = requests.get(url, timeout=5)

    assert response.status_code == 200
    assert "process_cpu_usage_percent" in response.text