Organization Management Service
===============================

Quick start
-----------

- Ensure Docker Desktop is installed and running (Windows/WSL2) or a Docker Engine is available.
- To bring the stack up with Docker Compose:

```powershell
docker-compose up --build
```

The API maps host port 9000 to container port 8000; the service will be reachable at http://localhost:9000.

Troubleshooting
---------------

- Error: `docker version` returns non-zero / returns an error
	- Make sure Docker Desktop is installed and running.
	- To start Docker Desktop from PowerShell (Admin):

```powershell
Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe" -Verb RunAs
```

	- Or run the diagnostic script `scripts\diagnose-docker.ps1` (open PowerShell as Administrator):

```powershell
cd <repo-root>\scripts
.\diagnose-docker.ps1
```

- Error: Port 9000 already in use
	- Detect which process uses port 9000: `Get-NetTCPConnection -LocalPort 9000 | Select-Object -Property LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess` (PowerShell)
	- Stop or kill the conflicting process or change `ports` in `docker-compose.yml`.

Run without Docker
------------------

If you want to run the service locally (Python environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd <repo-root>
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You can also use the helper script in `scripts\run-local.ps1`.

