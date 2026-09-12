# CC-0F4 - entorno reproducible CC-0F4

FROM pytorch/pytorch:2.11.0-cuda12.8-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JUPYTER_ENABLE_LAB=yes

WORKDIR /workspace/CC-0F4

COPY requirements.txt /tmp/requirements.txt


# 1. Verificar la imagen base

RUN echo "BASE PYTHON" \
    && which python \
    && python --version \
    && python -m pip --version \
    && python -c "import torch; print('torch base=', torch.__version__)"


# 2. Retirar dependencias incidentales de la imagen base
#
# spin no forma parte de CC-0F4 y restringe Click a < 8.4.
# Se elimina si esta presente para no condicionar las dependencias
# reales del curso.

RUN echo "LIMPIEZA BASE" \
    && if python -m pip show spin >/dev/null 2>&1; then \
           python -m pip uninstall \
               --break-system-packages \
               --yes \
               spin; \
       else \
           echo "spin no esta instalado"; \
       fi


# 3. Completar el stack PyTorch oficial 2.11.0
#
# La imagen base ya contiene torch 2.11.0 + CUDA 12.8.
# Se agregan las versiones compatibles de torchvision y torchaudio.

RUN echo "PYTORCH STACK" \
    && python -m pip install \
        --break-system-packages \
        --no-cache-dir \
        torchvision==0.26.0 \
        torchaudio==2.11.0 \
        --index-url https://download.pytorch.org/whl/cu128


# 4. Verificar PyTorch antes de instalar el resto del curso

RUN python -c "import torch, torchvision, torchaudio; \
actual=(torch.__version__.split('+')[0], \
torchvision.__version__.split('+')[0], \
torchaudio.__version__.split('+')[0]); \
expected=('2.11.0','0.26.0','2.11.0'); \
assert actual == expected, \
f'Stack PyTorch incorrecto: actual={actual}, esperado={expected}'; \
print('Stack PyTorch Docker: OK', actual)"


# 5. Instalar el stack global de CC-0F4

RUN echo "REQUIREMENTS CC-0F4" \
    && python -m pip install \
        --break-system-packages \
        --no-cache-dir \
        --upgrade-strategy only-if-needed \
        -r /tmp/requirements.txt


# 6. Verificar librerias principales

RUN echo "IMPORT CHECK" \
    && python -c "import nbconvert, nbformat, transformers, open_clip; \
import importlib.metadata as metadata; \
print('nbconvert=', nbconvert.__version__); \
print('nbformat=', nbformat.__version__); \
print('transformers=', transformers.__version__); \
print('open-clip-torch=', metadata.version('open-clip-torch')); \
print('OpenCLIP import: OK')"


# 7. Verificar que la instalacion del curso no altero PyTorch

RUN echo "PYTORCH FINAL CHECK" \
    && python -c "import torch, torchvision, torchaudio; \
actual=(torch.__version__.split('+')[0], \
torchvision.__version__.split('+')[0], \
torchaudio.__version__.split('+')[0]); \
expected=('2.11.0','0.26.0','2.11.0'); \
assert actual == expected, \
f'Stack PyTorch alterado: actual={actual}, esperado={expected}'; \
print('Stack PyTorch final: OK', actual)"


# 8. Verificar consistencia global de dependencias

RUN echo "PIP CHECK" \
    && python -m pip check


# 9. Confirmar que spin no reaparecio

RUN echo "SPIN CHECK" \
    && python -c "import importlib.util; \
assert importlib.util.find_spec('spin') is None, \
'spin no deberia estar instalado'; \
print('spin ausente: OK')"


# 10. Preparar el usuario no privilegiado existente
#
# La imagen base utiliza UID 1000 y GID 1000 para el usuario ubuntu.
# Se reutiliza en lugar de crear otro usuario con los mismos IDs.

RUN echo "USER SETUP" \
    && getent passwd 1000 \
    && getent group 1000 \
    && mkdir -p /workspace/CC-0F4 \
    && chown -R 1000:1000 /workspace/CC-0F4


USER 1000:1000

ENV HOME=/home/ubuntu

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--ServerApp.root_dir=/workspace/CC-0F4"]
