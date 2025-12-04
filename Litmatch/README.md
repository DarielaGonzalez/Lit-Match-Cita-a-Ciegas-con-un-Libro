# Lit-Match — Minimal Prototype

Proyecto prototipo para Lit-Match: Cita a Ciegas con Libros.

Estructura:
- `backend/`: API en FastAPI con endpoints para registro, login, cuestionario, feedback, autor y recomendaciones.
- `frontend/`: HTML/JS estático que consume la API.

Requisitos (backend): Python 3.10+

Instalación y ejecución (PowerShell):

```powershell
cd C:\Users\lilia\Documents\Litmatch\backend
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Abrir la UI estática:

```powershell
# Desde el directorio raíz abre el archivo HTML directamente en el navegador
start .\frontend\index.html
```

Notas:
- El motor de recomendación usa `sentence-transformers` para generar embeddings. En este prototipo las obras se guardan en SQLite y las incrustaciones como arrays serializados.
- Integraciones reales (Stripe, transportistas) están indicadas como stubs para implementar luego.
