### Entorno global de CC-0F4

#### Principio

CC-0F4 utiliza **un solo entorno de software para todo el semestre**.

Las semanas contienen material académico:

```text
SemanaN/
  ->
README
cuaderno
laboratorio, cuando corresponde
lecturas
material de exposición
datos didácticos
```

La infraestructura vive únicamente en la raíz:

```text
requirements.txt
Makefile
Dockerfile
ENTORNO.md
.gitattributes
.gitignore
```

No se crean entornos Python, Dockerfiles, requirements ni Makefiles por semana.

La regla es:

```text
una infraestructura global + material académico por semana
```

#### Dos entornos de ejecución

El curso mantiene dos entornos independientes:

```text
HOST
  -> .ccf04
  -> desarrollo y validación local

DOCKER
  -> imagen cc0f4:2026-2
  -> validación reproducible y ejecución aislada
```

`.ccf04` no se copia dentro de Docker.

Docker no utiliza el Python global del host ni el entorno `.ccf04`.

### Entorno Python local

#### Nombre del entorno

El entorno local recomendado es:

```text
.ccf04
```

Se crea una sola vez.

No debe versionarse y está excluido mediante `.gitignore`.

#### Crear el entorno en Linux o WSL

Desde la raíz del repositorio:

```bash
make setup
```

Activación:

```bash
source .ccf04/bin/activate
```

Verificación:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

#### Crear el entorno en Windows con PowerShell

Si `python` está disponible:

```powershell
make setup
```

Activación:

```powershell
.ccf04\Scripts\Activate.ps1
```

Verificación:

```powershell
python --version
python -c "import sys; print(sys.executable)"
```

#### Crear el entorno en Windows con Git Bash

Git Bash puede utilizarse como terminal principal del curso.

Primero verifica:

```bash
python --version
```

En algunas instalaciones de Windows, `python` o `python3` pueden resolver al alias de Microsoft Store.

Si está disponible el Python Launcher:

```bash
py -3 --version
```

crea el entorno explícitamente con:

```bash
make PYTHON="py -3" setup
```

Activa:

```bash
source .ccf04/Scripts/activate
```

Verifica:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

El ejecutable debe pertenecer al repositorio, por ejemplo:

```text
C:\Users\usuario\CC-0F4\.ccf04\Scripts\python.exe
```

Una vez activado `.ccf04`, se utiliza normalmente:

```bash
make install-cpu
make doctor
make check
```

No es necesario seguir escribiendo `PYTHON="py -3"` porque `python` ya apunta al entorno activo.

#### Stack PyTorch del semestre

PyTorch se mantiene fuera de `requirements.txt` porque la build depende del entorno de ejecución.

El stack fijado es:

```text
torch        2.11.0
torchvision  0.26.0
torchaudio   2.11.0
```

El Makefile instala las tres bibliotecas conjuntamente para impedir que una dependencia de alto nivel cambie silenciosamente la versión de PyTorch.

#### Instalación local CPU

Con `.ccf04` activado:

```bash
make install-cpu
```

El flujo es:

```text
PyTorch CPU -> torchvision + torchaudio compatibles -> requirements.txt -> verificación del stack -> pip check
```

#### Instalación local NVIDIA GPU

Con `.ccf04` activado:

```bash
make install-gpu
```

El flujo es:

```text
PyTorch CUDA 12.8 -> torchvision + torchaudio compatibles -> requirements.txt -> verificación del stack -> pip check
```

La disponibilidad real de GPU depende además del driver NVIDIA y del sistema operativo.



### Verificación del entorno local

Diagnóstico:

```bash
make doctor
```

Verificación explícita del stack PyTorch:

```bash
make verify-torch-stack
```

Resultado esperado:

```text
Stack PyTorch: OK ('2.11.0', '0.26.0', '2.11.0')
```

Consistencia de dependencias:

```bash
python -m pip check
```

Resultado esperado:

```text
No broken requirements found.
```

#### Validación estructural

Todas las semanas publicadas:

```bash
make check
```

`make check` descubre automáticamente las carpetas `SemanaN/` existentes y valida cada una.

Durante el desarrollo pueden existir semanas futuras todavía incompletas. Para validar únicamente un conjunto cerrado:

```bash
make CHECK_WEEKS="1 2 3 4" check
```

La diferencia conceptual es:

```text
make CHECK_WEEKS="1 2 3 4" check
  -> gate de release de semanas cerradas

make check
  -> estado estructural de todas las semanas publicadas
```

Para una semana:

```bash
make check-week WEEK=2
make check-semana2
```

Las reglas patrón permiten `make check-semanaN` sin editar el Makefile.


#### Ejecución local de notebooks

Forma explícita:

```bash
make execute-cuaderno WEEK=2
```

Forma abreviada:

```bash
make execute-cuaderno2
```

El resultado se escribe en `.build/`, que contiene artefactos regenerables y no se versiona.

Semana 3 sin descargar el LLM:

```bash
CC0F4_RUN_REAL_LLM=0 make execute-cuaderno3
```

Semana 4 sin descargar el encoder:

```bash
CC0F4_RUN_REAL_RETRIEVAL=0 make execute-cuaderno4
```

Estos modos sirven como smoke tests del software. No sustituyen los experimentos canónicos con el modelo o encoder real.

### Docker

#### Imagen global del curso

CC-0F4 utiliza una sola imagen para todo el semestre:

```text
cc0f4:2026-2
```

No se crea una imagen distinta por semana.

La misma imagen puede utilizarse para CPU, GPU NVIDIA y cualquier `SemanaN/`.

La imagen es CUDA-capable, pero CUDA solo es visible cuando el contenedor se crea exponiendo la GPU.

#### Imagen vs contenedor

Es importante distinguir:

```text
imagen:
cc0f4:2026-2

contenedor: instancia creada a partir de la imagen
```

En Docker Desktop, una fila como `cc0f4   2026-2` corresponde a la imagen. Todavía no implica que exista un contenedor ejecutándose.

#### Construir la imagen

```bash
make docker-build
```

Equivalente:

```bash
docker build --pull -t cc0f4:2026-2 .
```

#### Verificar la imagen

```bash
docker image ls cc0f4:2026-2
```

CPU:

```bash
make docker-check-cpu
```

Sin `--gpus all`, es correcto obtener:

```text
cuda_available= False
device= CPU
```

La build instalada puede seguir siendo `torch=2.11.0+cu128`. Esto significa que la imagen contiene soporte CUDA, no que una GPU haya sido expuesta al contenedor.

GPU:

```bash
make docker-check-gpu
```

#### Convención de nombres de contenedores

La imagen sigue siendo siempre:

```text
cc0f4:2026-2
```

Si solo se utiliza un contenedor persistente:

```text
cc0f4
```

Si se desea identificar semana y dispositivo:

```text
cc0f4-w01-cpu
cc0f4-w01-gpu
cc0f4-w02-cpu
cc0f4-w04-gpu
```

Convención recomendada:

```text
cc0f4-wNN-cpu
cc0f4-wNN-gpu
```

No es obligatorio crear un contenedor por semana. Un único contenedor `cc0f4` puede utilizar todas las semanas porque el repositorio completo se monta en `/workspace/CC-0F4`.

Los nombres por semana son útiles cuando se desean mantener varios contenedores simultáneamente o identificar claramente una sesión.

#### Contenedores efímeros y persistentes

Los targets actuales:

```bash
make docker-run-cpu
make docker-run-gpu
```

utilizan `--rm`, por lo que crean contenedores efímeros.

Para uso diario con Docker Desktop puede ser más cómodo crear un contenedor persistente con `--name`.

### Windows + Docker Desktop

#### Requisitos

Para CPU:

```text
Docker Desktop
backend Linux containers
repositorio clonado
imagen cc0f4:2026-2 construida
```

Para GPU NVIDIA se requiere además:

```text
Docker Desktop con backend WSL2
driver NVIDIA compatible
soporte GPU funcional en WSL2/Docker
```

#### Windows Git Bash: tratamiento de rutas

Git Bash utiliza MSYS y puede transformar automáticamente rutas Unix.

Una ruta destinada al contenedor como `/workspace/CC-0F4` puede convertirse incorrectamente en algo semejante a `C:/Program Files/Git/workspace/CC-0F4`.

Para comandos Docker manuales:

```bash
export MSYS_NO_PATHCONV=1
HOST_REPO="$(pwd -W)"
```

Comprueba:

```bash
echo "$HOST_REPO"
```

Debe obtenerse algo semejante a:

```text
C:/Users/usuario/CC-0F4
```

El Makefile ya aplica `MSYS_NO_PATHCONV=1` en `docker-test-cuaderno`.

#### Windows Git Bash: contenedor persistente CPU

Ejemplo para Semana 1:

```bash
export MSYS_NO_PATHCONV=1
HOST_REPO="$(pwd -W)"

docker rm -f cc0f4-w01-cpu 2>/dev/null || true

docker run -d \
  --name cc0f4-w01-cpu \
  --shm-size=2g \
  -p 8881:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```

JupyterLab:

```text
http://localhost:8881
```

Logs:

```bash
docker logs cc0f4-w01-cpu
```

Shell:

```bash
docker exec -it cc0f4-w01-cpu bash
```

Verificación:

```bash
docker exec cc0f4-w01-cpu \
  python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

En CPU, `False` es el resultado correcto.

#### Windows Git Bash: contenedor persistente GPU

```bash
export MSYS_NO_PATHCONV=1
HOST_REPO="$(pwd -W)"

docker rm -f cc0f4-w01-gpu 2>/dev/null || true

docker run -d \
  --name cc0f4-w01-gpu \
  --gpus all \
  --shm-size=2g \
  -p 8881:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```

Verificación:

```bash
docker exec cc0f4-w01-gpu \
  python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'GPU no disponible')"
```

Se espera `True` y el nombre de la GPU.

#### Windows PowerShell: contenedor CPU

PowerShell no necesita `MSYS_NO_PATHCONV`.

```powershell
docker rm -f cc0f4-w01-cpu 2>$null

docker run -d `
  --name cc0f4-w01-cpu `
  --shm-size=2g `
  -p 8881:8888 `
  -v "${PWD}:/workspace/CC-0F4" `
  cc0f4:2026-2
```

#### Windows PowerShell: contenedor GPU

```powershell
docker rm -f cc0f4-w01-gpu 2>$null

docker run -d `
  --name cc0f4-w01-gpu `
  --gpus all `
  --shm-size=2g `
  -p 8881:8888 `
  -v "${PWD}:/workspace/CC-0F4" `
  cc0f4:2026-2
```
### Linux

#### Diferencia principal respecto de Windows

En Linux no existe la conversión de rutas de Git Bash/MSYS.

Se utiliza directamente:

```bash
HOST_REPO="$(pwd)"
```

No se necesita `MSYS_NO_PATHCONV`, `pwd -W` ni Docker Desktop. Docker puede ejecutarse mediante Docker Engine.

#### Linux CPU

```bash
HOST_REPO="$(pwd)"

docker rm -f cc0f4-w01-cpu 2>/dev/null || true

docker run -d \
  --name cc0f4-w01-cpu \
  --shm-size=2g \
  -p 8881:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```

#### Linux GPU NVIDIA

El host debe tener driver NVIDIA, Docker Engine y NVIDIA Container Toolkit.

Primero:

```bash
nvidia-smi
```

Prueba Docker GPU:

```bash
docker run --rm --gpus all \
  cc0f4:2026-2 \
  python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Contenedor persistente:

```bash
HOST_REPO="$(pwd)"

docker rm -f cc0f4-w01-gpu 2>/dev/null || true

docker run -d \
  --name cc0f4-w01-gpu \
  --gpus all \
  --shm-size=2g \
  -p 8881:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```
#### Un solo contenedor para todo el curso

Si no se necesita distinguir semanas, puede utilizarse siempre el nombre `cc0f4`.

#### Windows Git Bash CPU

```bash
export MSYS_NO_PATHCONV=1
HOST_REPO="$(pwd -W)"

docker rm -f cc0f4 2>/dev/null || true

docker run -d \
  --name cc0f4 \
  --shm-size=2g \
  -p 8888:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```

#### Windows Git Bash GPU

```bash
export MSYS_NO_PATHCONV=1
HOST_REPO="$(pwd -W)"

docker rm -f cc0f4 2>/dev/null || true

docker run -d \
  --name cc0f4 \
  --gpus all \
  --shm-size=2g \
  -p 8888:8888 \
  -v "${HOST_REPO}:/workspace/CC-0F4" \
  cc0f4:2026-2
```

#### Linux CPU

```bash
docker rm -f cc0f4 2>/dev/null || true

docker run -d \
  --name cc0f4 \
  --shm-size=2g \
  -p 8888:8888 \
  -v "$(pwd):/workspace/CC-0F4" \
  cc0f4:2026-2
```

#### Linux GPU

```bash
docker rm -f cc0f4 2>/dev/null || true

docker run -d \
  --name cc0f4 \
  --gpus all \
  --shm-size=2g \
  -p 8888:8888 \
  -v "$(pwd):/workspace/CC-0F4" \
  cc0f4:2026-2
```

#### CPU y GPU con la misma imagen

La imagen `cc0f4:2026-2` es la misma.

CPU:

```text
docker run ...
```

GPU:

```text
docker run --gpus all ...
```

Un contenedor creado sin `--gpus all` no puede adquirir GPU posteriormente mediante `docker start`.

Para cambiarlo debe detenerse, eliminarse y recrearse con `--gpus all`.

Una instancia creada con `--gpus all` sí puede ejecutar código que explícitamente seleccione CPU.


#### Varios contenedores simultáneos

Cada contenedor necesita un nombre distinto y, si expone Jupyter, un puerto distinto.

Ejemplo:

```text
cc0f4-w01-cpu -> localhost:8881
cc0f4-w02-cpu -> localhost:8882
cc0f4-w04-gpu -> localhost:8884
```

No pueden existir dos contenedores con el mismo nombre ni publicar simultáneamente el mismo puerto del host.

#### Operación diaria de un contenedor persistente

Listar:

```bash
docker ps -a
```

Iniciar:

```bash
docker start cc0f4
```

Detener:

```bash
docker stop cc0f4
```

Logs:

```bash
docker logs cc0f4
```

Seguir logs:

```bash
docker logs -f cc0f4
```

Entrar:

```bash
docker exec -it cc0f4 bash
```

Eliminar:

```bash
docker rm -f cc0f4
```

Eliminar el contenedor no elimina la imagen. El repositorio tampoco se pierde porque está montado desde el host.


#### JupyterLab dentro del contenedor

El Dockerfile inicia JupyterLab en `0.0.0.0:8888`.

Si el contenedor publica `-p 8888:8888`, se accede desde:

```text
http://localhost:8888
```

Si publica `-p 8881:8888`, se accede desde:

```text
http://localhost:8881
```

El token puede consultarse con:

```bash
docker logs cc0f4
```

#### Prueba Docker de un cuaderno

El Makefile proporciona:

```bash
make docker-test-cuaderno2
```

La regla patrón permite cualquier semana futura.

El target crea un contenedor transitorio, ejecuta el cuaderno y escribe el resultado en `.build/`.

En Git Bash, el target ya deshabilita la conversión MSYS de rutas mediante `MSYS_NO_PATHCONV=1`.

#### Variables de ejecución dentro de Docker

Una variable definida únicamente en el host no entra automáticamente al contenedor.

Debe pasarse mediante:

```text
docker run -e VARIABLE=valor
```

o:

```text
docker exec -e VARIABLE=valor
```

Semana 3 offline dentro de un contenedor persistente:

```bash
docker exec \
  -e CC0F4_RUN_REAL_LLM=0 \
  cc0f4 \
  python -m nbconvert \
    --to notebook \
    --execute /workspace/CC-0F4/Semana3/Cuaderno3-CC-0F4.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output-dir=/workspace/CC-0F4/.build \
    --output=Cuaderno3-CC-0F4.docker.executed.ipynb
```

Semana 4 offline:

```bash
docker exec \
  -e CC0F4_RUN_REAL_RETRIEVAL=0 \
  cc0f4 \
  python -m nbconvert \
    --to notebook \
    --execute /workspace/CC-0F4/Semana4/Cuaderno4-CC-0F4.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output-dir=/workspace/CC-0F4/.build \
    --output=Cuaderno4-CC-0F4.docker.executed.ipynb
```

Laboratorio 4 offline:

```bash
docker exec \
  -e CC0F4_RUN_REAL_RETRIEVAL=0 \
  cc0f4 \
  python -m nbconvert \
    --to notebook \
    --execute /workspace/CC-0F4/Semana4/Laboratorio4-CC-0F4.ipynb \
    --ExecutePreprocessor.timeout=600 \
    --output-dir=/workspace/CC-0F4/.build \
    --output=Laboratorio4-CC-0F4.docker.executed.ipynb
```

#### Persistencia

El repositorio del host se monta mediante:

```text
-v HOST_REPO:/workspace/CC-0F4
```

Por tanto:

```text
edición en host
  <->
archivo visible dentro del contenedor
```

Los cambios al repositorio permanecen aunque el contenedor se elimine.

Los paquetes instalados manualmente dentro de un contenedor sí se pierden al eliminarlo. Por reproducibilidad no se recomienda modificar dependencias manualmente dentro del contenedor.

Si cambia `requirements.txt` o `Dockerfile`, se reconstruye la imagen y se recrea el contenedor.

#### Tamaño de la imagen

La imagen puede ocupar varios GB porque contiene CUDA runtime, PyTorch, torchvision, torchaudio, Jupyter, Transformers, OpenCLIP, FAISS y el stack científico.

Una imagen de más de 10 GB no implica por sí sola un error.

Debe distinguirse entre imagen Docker, contenedor, cache del builder, modelos descargados y datasets descargados.

#### Limpieza

Artefactos del curso:

```bash
make clean
```
Contenedores:

```bash
docker ps -a
docker rm -f cc0f4
```

Cache del builder:

```bash
docker builder prune
```

Imágenes no utilizadas:

```bash
docker image prune
```

No se recomienda utilizar rutinariamente `docker system prune -a` porque puede eliminar imágenes útiles de otros proyectos.

#### Windows: finales de línea

El repositorio utiliza `.gitattributes` para normalizar archivos de texto a LF.

Git Bash puede mostrar:

```text
CRLF will be replaced by LF the next time Git touches it
```

Ese mensaje es informativo y no representa un fallo de `git diff --check`.

No es necesario ejecutar `git add --renormalize .` salvo que se desee deliberadamente normalizar todo el repositorio.

#### Modelos y datasets externos

`requirements.txt` instala bibliotecas, no todos los pesos de modelos ni datasets grandes.

Debe distinguirse:

```text
dependencia de software != artefacto descargable
```

Un modelo de Hugging Face, dataset o checkpoint puede estar en cache, descargarse en la primera ejecución u omitirse en un smoke test offline.

No debe ser razón para crear un entorno distinto por semana.

#### Reproducibilidad

Todo experimento debe registrar, cuando corresponda:

```text
Python
PyTorch
torchvision
torchaudio
librerías relevantes
CPU/GPU
modelo
revisión del modelo
seed
datos
prompt
configuración
métrica
resultado
```

Para inferencia también:

```text
decoding
context length
batch
precision
KV heads
unidad de memoria
supuestos del estimador
```

#### Gate recomendado antes de cerrar una semana

Validación estructural:

```bash
make check-semanaN
```

Ejecución local:

```bash
make execute-cuadernoN
```

Ejecución Docker:

```bash
make docker-test-cuadernoN
```

Cuando la semana requiera recursos externos, debe existir una distinción explícita entre smoke test offline y experimento canónico real.

Un smoke test demuestra que el software ejecuta. No demuestra por sí solo la conclusión experimental.

#### Regla para el resto del semestre

Al crear `Semana5/`, `Semana6/`, ..., `Semana16/` se agregan materiales académicos.

No se agregan:

```text
nuevo entorno Python
nuevo Makefile
nuevo Dockerfile
requirements de la semana
imagen Docker de la semana
```

Si una dependencia realmente nueva fuera imprescindible y no pudo preverse en el stack global, se trata como una modificación excepcional de infraestructura del curso.

Después se vuelve a validar host + Docker antes de dar por cerrada la nueva semana.
