# Makefile

VENV_DIR ?= .ccf04
SYSTEM_PYTHON ?= python

ifeq ($(OS),Windows_NT)
VENV_PYTHON := $(VENV_DIR)/Scripts/python.exe
else
VENV_PYTHON := $(VENV_DIR)/bin/python
endif

# Por defecto, todas las tareas Python usan el entorno local del repositorio.
# Puede sobrescribirse explicitamente desde la linea de comandos:
#
# make PYTHON=/ruta/a/python doctor
PYTHON := $(VENV_PYTHON)
PIP := $(PYTHON) -m pip

TORCH_VERSION ?= 2.11.0
TORCHVISION_VERSION ?= 0.26.0
TORCHAUDIO_VERSION ?= 2.11.0

TORCH_CPU_INDEX ?= https://download.pytorch.org/whl/cpu
TORCH_CUDA_INDEX ?= https://download.pytorch.org/whl/cu128

IMAGE ?= cc0f4:2026-2
WORKDIR ?= $(CURDIR)
BUILD_DIR ?= .build
NOTEBOOK_TIMEOUT ?= 600

# Si se define, check valida solo estas semanas.
# Ejemplo:
# make CHECK_WEEKS="1 2 3 4 5" check
CHECK_WEEKS ?=

WEEK ?= 1
WEEK_DIR := Semana$(WEEK)
CUADERNO := $(WEEK_DIR)/Cuaderno$(WEEK)-CC-0F4.ipynb
LABORATORIO := $(WEEK_DIR)/Laboratorio$(WEEK)-CC-0F4.ipynb

# Semanas que deliberadamente no tienen laboratorio canonico.
# Semana 3 usa el jueves completo para la evaluacion oral E1.
# Semana 5 usa el jueves completo para la evaluacion oral E2.
# Semana 6 no tiene laboratorio por el feriado del jueves 8 de octubre.
NO_LAB_WEEKS ?= 3 5 6

.PHONY: help setup require-python \
	install-cpu install-gpu install-course verify-torch-stack doctor \
	check check-root check-week validate-notebooks validate-week \
	execute-cuaderno \
	docker-build docker-check-cpu docker-check-gpu \
	docker-run-cpu docker-run-gpu docker-test-cuaderno \
	clean FORCE


help:
	@echo "CC-0F4 - entorno global del curso"
	@echo ""
	@echo "Entorno:"
	@echo "  make setup"
	@echo "      Crea el unico entorno local $(VENV_DIR)"
	@echo ""
	@echo "  El resto de targets usa automaticamente:"
	@echo "      $(VENV_PYTHON)"
	@echo ""
	@echo "  No es necesario activar $(VENV_DIR) antes de usar make."
	@echo ""
	@echo "Instalacion:"
	@echo "  make install-cpu"
	@echo "      Instala PyTorch CPU + stack completo"
	@echo ""
	@echo "  make install-gpu"
	@echo "      Instala PyTorch CUDA 12.8 + stack completo"
	@echo ""
	@echo "  make verify-torch-stack"
	@echo "      Verifica versiones del stack PyTorch"
	@echo ""
	@echo "  make doctor"
	@echo "      Muestra interprete, entorno, GPU y versiones principales"
	@echo ""
	@echo "Validacion:"
	@echo "  make check"
	@echo "      Verifica todas las semanas existentes"
	@echo ""
	@echo "  make CHECK_WEEKS=\"1 2 3 4 5\" check"
	@echo "      Verifica solo las semanas indicadas"
	@echo ""
	@echo "  make check-week WEEK=2"
	@echo "  make check-semana2"
	@echo "  make validate-notebooks"
	@echo ""
	@echo "Ejecucion:"
	@echo "  make execute-cuaderno WEEK=2"
	@echo "  make execute-cuaderno2"
	@echo ""
	@echo "  CC0F4_RUN_REAL_LLM=0 make execute-cuaderno3"
	@echo "  CC0F4_RUN_REAL_RETRIEVAL=0 make execute-cuaderno4"
	@echo ""
	@echo "  CC0F4_RUN_REAL_RETRIEVAL=0 \\"
	@echo "  CC0F4_RUN_REAL_RERANKER=0 \\"
	@echo "  CC0F4_RUN_REAL_LLM=0 \\"
	@echo "    make execute-cuaderno5"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build"
	@echo "  make docker-check-cpu"
	@echo "  make docker-check-gpu"
	@echo "  make docker-run-cpu"
	@echo "  make docker-run-gpu"
	@echo "  make docker-test-cuaderno2"
	@echo ""
	@echo "Limpieza:"
	@echo "  make clean"


setup:
	@test ! -d "$(VENV_DIR)" || { \
		echo "ERROR: $(VENV_DIR) ya existe."; \
		echo "No es necesario recrearlo."; \
		echo "Verifica el entorno con: make doctor"; \
		exit 1; \
	}
	@command -v "$(SYSTEM_PYTHON)" >/dev/null 2>&1 || { \
		echo "ERROR: no se encontro $(SYSTEM_PYTHON)."; \
		exit 1; \
	}
	$(SYSTEM_PYTHON) -m venv "$(VENV_DIR)"
	@"$(VENV_PYTHON)" -m pip --version
	@echo ""
	@echo "Entorno creado: $(VENV_DIR)"
	@echo ""
	@echo "Los comandos make usaran automaticamente:"
	@echo "  $(VENV_PYTHON)"
	@echo ""
	@echo "No necesitas activar el entorno para usar make."
	@echo ""
	@echo "Para trabajo interactivo puedes activarlo:"
	@echo ""
	@echo "  Linux/WSL:"
	@echo "    source $(VENV_DIR)/bin/activate"
	@echo ""
	@echo "  Windows Git Bash:"
	@echo "    source $(VENV_DIR)/Scripts/activate"
	@echo ""
	@echo "  Windows PowerShell:"
	@echo "    .\\$(VENV_DIR)\\Scripts\\Activate.ps1"


require-python:
	@command -v "$(PYTHON)" >/dev/null 2>&1 || { \
		echo "ERROR: no se encontro el interprete del entorno:"; \
		echo "  $(PYTHON)"; \
		echo ""; \
		echo "Crea primero el entorno con:"; \
		echo "  make setup"; \
		exit 1; \
	}


# PyTorch, torchvision y torchaudio se fijan conjuntamente.
# Esto evita que una dependencia como open-clip-torch instale una
# torchvision mas reciente que termine actualizando torch.
install-cpu: require-python
	$(PIP) install --upgrade pip
	$(PIP) install \
		torch==$(TORCH_VERSION) \
		torchvision==$(TORCHVISION_VERSION) \
		torchaudio==$(TORCHAUDIO_VERSION) \
		--index-url $(TORCH_CPU_INDEX)
	$(MAKE) --no-print-directory install-course
	$(MAKE) --no-print-directory verify-torch-stack
	$(PIP) check


install-gpu: require-python
	$(PIP) install --upgrade pip
	$(PIP) install \
		torch==$(TORCH_VERSION) \
		torchvision==$(TORCHVISION_VERSION) \
		torchaudio==$(TORCHAUDIO_VERSION) \
		--index-url $(TORCH_CUDA_INDEX)
	$(MAKE) --no-print-directory install-course
	$(MAKE) --no-print-directory verify-torch-stack
	$(PIP) check


# only-if-needed es tambien la estrategia normal de pip, pero se declara
# explicitamente porque el stack PyTorch ya fue seleccionado arriba.
install-course: require-python
	$(PIP) install \
		--upgrade-strategy only-if-needed \
		-r requirements.txt


verify-torch-stack: require-python
	$(PYTHON) -c "import torch, torchvision, torchaudio; \
	actual=(torch.__version__.split('+')[0], torchvision.__version__.split('+')[0], torchaudio.__version__.split('+')[0]); \
	expected=('$(TORCH_VERSION)', '$(TORCHVISION_VERSION)', '$(TORCHAUDIO_VERSION)'); \
	assert actual == expected, f'Stack PyTorch incorrecto: actual={actual}, esperado={expected}'; \
	print('Stack PyTorch: OK', actual)"


doctor: require-python
	@echo "python_cmd=$(PYTHON)"
	$(PYTHON) -c "import sys; print('python=', sys.version.split()[0]); print('executable=', sys.executable); print('prefix=', sys.prefix)"
	$(PYTHON) -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device_count=', torch.cuda.device_count()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
	$(PYTHON) -c "import torchvision, torchaudio; print('torchvision=', torchvision.__version__); print('torchaudio=', torchaudio.__version__)"
	$(PYTHON) -c "import transformers, numpy, pandas; print('transformers=', transformers.__version__); print('numpy=', numpy.__version__); print('pandas=', pandas.__version__)"
	$(PYTHON) -c "import nbformat, nbconvert; print('nbformat=', nbformat.__version__); print('nbconvert=', nbconvert.__version__)"


check-root:
	@test -f README.md
	@test -f LICENSE
	@test -f requirements.txt
	@test -f Makefile
	@test -f Dockerfile
	@test -f ENTORNO.md
	@echo "Raiz del curso: OK"


check: check-root
	@set -e; \
	if [ -n "$(strip $(CHECK_WEEKS))" ]; then \
		for num in $(CHECK_WEEKS); do \
			case "$$num" in \
				''|*[!0-9]*) \
					echo "Semana invalida en CHECK_WEEKS: $$num"; \
					exit 1 ;; \
			esac; \
			$(MAKE) --no-print-directory check-week WEEK="$$num"; \
		done; \
		echo "Semanas solicitadas: OK"; \
	else \
		found=0; \
		for dir in Semana[0-9]*; do \
			[ -d "$$dir" ] || continue; \
			num=$${dir#Semana}; \
			case "$$num" in \
				''|*[!0-9]*) continue ;; \
			esac; \
			found=1; \
			$(MAKE) --no-print-directory check-week WEEK="$$num"; \
		done; \
		if [ $$found -eq 0 ]; then \
			echo "No se encontraron carpetas SemanaN."; \
			exit 1; \
		fi; \
		echo "Todas las semanas existentes: OK"; \
	fi


check-week:
	@test -d "$(WEEK_DIR)"
	@test -f "$(WEEK_DIR)/README.md"
	@test -f "$(CUADERNO)"
	@case " $(NO_LAB_WEEKS) " in \
		*" $(WEEK) "*) \
			echo "$(WEEK_DIR): sin laboratorio canonico" ;; \
		*) \
			test -f "$(LABORATORIO)" ;; \
	esac
	@$(MAKE) --no-print-directory validate-week WEEK=$(WEEK)
	@echo "$(WEEK_DIR): estructura y notebooks OK"


validate-notebooks: require-python
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('.').glob('Semana[0-9]*/*.ipynb')); assert ps, 'No hay notebooks'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'nbformat: {len(ps)} notebooks OK')"


validate-week: require-python
	$(PYTHON) -c "from pathlib import Path; import nbformat; ps=sorted(Path('$(WEEK_DIR)').glob('*.ipynb')); assert ps, 'No hay notebooks en $(WEEK_DIR)'; [nbformat.validate(nbformat.read(str(p), as_version=4)) for p in ps]; print(f'$(WEEK_DIR): {len(ps)} notebooks nbformat OK')"


execute-cuaderno: require-python
	@test -f "$(CUADERNO)"
	@mkdir -p $(BUILD_DIR)
	$(PYTHON) -m nbconvert \
		--to notebook \
		--execute "$(CUADERNO)" \
		--ExecutePreprocessor.timeout=$(NOTEBOOK_TIMEOUT) \
		--output "$(CURDIR)/$(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.executed.ipynb"
	@echo "Cuaderno ejecutado: $(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.executed.ipynb"


# Reglas patron: no se agregan targets por semana.
check-semana%: FORCE
	@$(MAKE) --no-print-directory check-week WEEK=$*


execute-cuaderno%: FORCE
	@$(MAKE) --no-print-directory execute-cuaderno WEEK=$*


docker-test-cuaderno%: FORCE
	@$(MAKE) --no-print-directory docker-test-cuaderno WEEK=$*


docker-build:
	docker build --pull -t $(IMAGE) .


docker-check-cpu:
	docker run --rm $(IMAGE) \
		python -c "import torch; print('torch=', torch.__version__); print('cuda_available=', torch.cuda.is_available()); print('device=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"


docker-check-gpu:
	docker run --rm --gpus all $(IMAGE) \
		python -c "import torch; assert torch.cuda.is_available(), 'CUDA no disponible dentro del contenedor'; print('torch=', torch.__version__); print('gpu=', torch.cuda.get_device_name(0)); print('device_count=', torch.cuda.device_count())"


docker-run-cpu:
	docker run --rm -it \
		--shm-size=2g \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)


docker-run-gpu:
	docker run --rm -it \
		--gpus all \
		--shm-size=2g \
		-p 8888:8888 \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE)


docker-test-cuaderno:
	@test -f "$(CUADERNO)"
	@mkdir -p $(BUILD_DIR)
	MSYS_NO_PATHCONV=1 docker run --rm \
		--shm-size=2g \
		-v "$(WORKDIR):/workspace/CC-0F4" \
		$(IMAGE) \
		python -m nbconvert \
			--to notebook \
			--execute "/workspace/CC-0F4/$(CUADERNO)" \
			--ExecutePreprocessor.timeout=$(NOTEBOOK_TIMEOUT) \
			--output "/workspace/CC-0F4/$(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"
	@echo "Cuaderno ejecutado en Docker: $(BUILD_DIR)/Cuaderno$(WEEK)-CC-0F4.docker.executed.ipynb"


clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ipynb_checkpoints' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BUILD_DIR)


FORCE:
