# CC-0F4 — Guía de ejecución (Docker)

Puesta en marcha de los notebooks del curso **CC-0F4** desde cero, usando el contenedor Docker oficial. Funciona igual en Windows, macOS y Linux, y **no requiere GPU** (corre en CPU).

## Requisitos previos
- **Docker Desktop** instalado y **abierto** (icono en estado *running*).
  - Windows 11: `winget install -e --id Docker.DockerDesktop`
- **Git**.
- ~20 GB de disco libres.

## 1. Clonar el repositorio
```bash
git clone https://github.com/kapumota/CC-0F4
cd CC-0F4
```

## 2. Construir la imagen (~15–40 min la primera vez)
```bash
docker build --pull -t cc0f4:2026-2 .
```
El Dockerfile verifica el stack por sí mismo; si termina sin error, la imagen quedó correcta.

## 3. Levantar JupyterLab

**Windows (PowerShell):**
```powershell
docker run --rm -it --shm-size=2g -p 8888:8888 -v "${PWD}:/workspace/CC-0F4" cc0f4:2026-2
```

**macOS / Linux:**
```bash
docker run --rm -it --shm-size=2g -p 8888:8888 -v "$(pwd):/workspace/CC-0F4" cc0f4:2026-2
```

## 4. Abrir en el navegador
La terminal imprime una URL con token al arrancar. Copia la que empieza por:
```
http://127.0.0.1:8888/lab?token=...
```
No cierres esa terminal: mantiene vivo el servidor.

## 5. Ejecutar y verificar
Abre `Semana1/Cuaderno1-CC-0F4.ipynb` y ejecuta. La primera celda debe reportar el entorno correcto:
```python
import torch, platform
print(torch.__version__, "|", platform.system())   # -> 2.11.0+cu128 | Linux
```

## Volver a entrar después
La imagen ya está construida: repite solo el **paso 3**. El trabajo se guarda en tu carpeta porque está montada con `-v`.

## Trampas frecuentes
1. **No abras otro Jupyter local** (venv/Anaconda) mientras el contenedor corre: pelean por el puerto 8888. Si `docker run` dice *"port already allocated"*, cierra lo que use el 8888.
2. **Usa el token del contenedor** (el que aparece en esa terminal), no uno anterior.
3. En Windows, un `.venv` local puede fallar al importar torch con `WinError 1114`; por eso usamos Docker: es el entorno oficial del curso y es idéntico en cualquier laptop.

> Nota: no envíes soluciones por pull request al repositorio del curso.
