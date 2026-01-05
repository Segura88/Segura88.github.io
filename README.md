# Segura88.github.io

# Memories — Quickstart (consolidado)

Este README agrupa las instrucciones para desarrollo del backend y frontend, cómo probar en móvil y cómo ejecutar el script E2E.

Prerequisitos
- Python 3.11+ y pip
- Node.js + npm (para el frontend). Si npm no está en PATH incluimos cómo arrancar usando la ruta completa.

1) Abrir proyecto

```powershell
cd "C:\Users\jaime\OneDrive - Fundación Universitaria San Pablo CEU\Investigación-Docencia\Memories"
```

2) Backend — entorno Python

```powershell
# Crear (una sola vez)
python -m venv venv

# Activar (cada sesión)
.\venv\Scripts\Activate.ps1

# Si PowerShell bloquea la activación (solo una vez):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias (una vez)
pip install -r requirements.txt
```

Si no tienes `requirements.txt`, instala las dependencias mínimas:

```powershell
pip install fastapi uvicorn sqlalchemy pytz
```

Arrancar el backend (desarrollo):

```powershell
python -m uvicorn app.main:app --reload
```

La API estará en: http://127.0.0.1:8000
Documentación (Swagger): http://127.0.0.1:8000/docs

---

3) Frontend — Vite + React

En una nueva terminal (no hace falta activar el venv):

```powershell
cd .\frontend
```

Si `npm` está disponible en tu PATH:

```powershell
npm install
npm run dev -- --host
```

Si `npm` no está en PATH pero Node está instalado en `C:\Program Files\nodejs`, ejecuta:

```powershell
"C:\Program Files\nodejs\npm.cmd" install
"C:\Program Files\nodejs\npm.cmd" run dev -- --host
```

La opción `--host` hace que Vite escuche en la red local (útil para probar desde el móvil). Vite mostrará la URL local y la de red (ej. http://192.168.x.y:5173).

---

4) Probar en móvil (rápido)

- Emulación rápida: abre la app en el navegador de tu escritorio (http://localhost:5173) y activa DevTools (F12) → Device Toolbar (Ctrl+Shift+M).

4b) Probar en móvil real (misma Wi‑Fi)

1. Arranca Vite con `--host`.
2. Averigua la IP local de tu PC (PowerShell):

```powershell
ipconfig | Select-String 'IPv4'
# copia la IP del adaptador Wi‑Fi (ej. 192.168.1.42)
```

3. En el móvil (con la misma red Wi‑Fi) abre:

http://<TU_IP_LOCAL>:5173/

Si hay problemas de conexión revisa firewall o usa la ruta directa a `npm.cmd` como se muestra arriba.

---

5) Probar el flujo token → escribir desde móvil

- Genera un token desde la máquina (con venv activo):

```powershell
python -c "import sys; sys.path.append(r'.'); from app.tokens import generate_email_token; print(generate_email_token('Jaime'))"
```

- Copia la URL:

http://<TU_IP_LOCAL>:5173/write?token=PASTE_TOKEN

- Abre la URL en el móvil o crea un QR con:

```
https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=http://<TU_IP_LOCAL>:5173/write?token=PASTE_TOKEN
```

---

6) Script E2E (automático)

Hay un script PowerShell que arranca uvicorn, espera /health, genera token y ejecuta un POST de prueba:

```powershell
.\scripts\e2e_test.ps1
```

Úsalo desde la raíz del proyecto (con venv activado). El script arranca y detiene uvicorn automáticamente.

---

7) Debug / npm not found

- Comprueba si `npm` está en PATH:

```powershell
Get-Command npm -ErrorAction SilentlyContinue
where.exe npm
```

- Si no está, ejecuta `npm` usando la ruta completa:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' run dev -- --host
```

---

8) Limpiar / resetear DB (cuidado)

```powershell
# Asegúrate de detener uvicorn primero
Remove-Item .\memories.db
```

---

9) Tests

```powershell
pip install pytest
pytest -q
```

---

Notas de seguridad y despliegue
- No dejes ALLOW_WRITE ni TEST_NOW habilitados en producción. Estos atajos fueron añadidos para pruebas locales.
- Guarda las credenciales SMTP y secretos en variables de entorno, no en ficheros en el repo.

Admin login (opcional, discreto)
- Puedes habilitar un login de administración discreto (accedible haciendo doble-clic en el logo del splash) estableciendo dos variables de entorno:
	- `ADMIN_USER` — nombre de usuario (ej. "admin").
	- `ADMIN_PASSWORD_HASH` — hash bcrypt de la contraseña (no almacenar la contraseña en texto claro).

Generar un hash bcrypt con Python (ejemplo):

```powershell
python - <<'PY'
from passlib.context import CryptContext
pw = CryptContext(schemes=["bcrypt"]) 
print(pw.hash('mi-contraseña-segura'))
PY
```

En PowerShell puedes establecer las variables para la sesión actual:

```powershell
$env:ADMIN_USER = 'admin'
$env:ADMIN_PASSWORD_HASH = '<pega-el-hash-aqui>'
```

La API expone `/admin/login` (POST) que devuelve un token admin (JWT corto) y `/admin/ping` para verificar el token. En producción asegúrate de servir la app con HTTPS y manejar secretos con un gestor de secretos.

---

¿Quieres que también actualice `frontend/README.md` con un extracto corto y el comando para arrancar con la ruta completa de npm? Puedo añadirlo ahora.
