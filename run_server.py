"""
Run the CFS-HRV Monitor API server.

Usage:
    python run_server.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=4777,
        reload=True,
        log_level="info"
    )
