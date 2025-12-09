"""
Run the CFS-HRV Monitor API server with HTTPS.

Usage:
    python run_server.py
"""
import uvicorn
import os

if __name__ == "__main__":
    # Get certificate paths
    cert_path = os.path.join(os.path.dirname(__file__), "certs", "cert.pem")
    key_path = os.path.join(os.path.dirname(__file__), "certs", "key.pem")

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=4777,
        reload=True,
        log_level="info",
        ssl_keyfile=key_path,
        ssl_certfile=cert_path
    )
