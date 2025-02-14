# ------------------------------------
# envs
# ------------------------------------
VENV := venv
PYTHON := $(VENV)/bin/python

# ------------------------------------
# default
# ------------------------------------
.DEFAULT_GOAL := help

# ------------------------------------
# targets
# ------------------------------------
.PHONY: help install test clean run-server run-invoice-issuer \
        run-invoice-scheduler docker-build docker-run docker-stop

# ------------------------------------
# helps
# ------------------------------------
help:
	@echo "Makefile - Comandos disponíveis:"
	@echo ""
	@echo "  make install              Cria/atualiza o ambiente virtual e instala dependências"
	@echo "  make test                 Executa testes (pytest)"
	@echo "  make run-server           Inicia o servidor uvicorn em modo de desenvolvimento"
	@echo "  make run-invoice-issuer   Executa o worker de invoice_issuer em modo de desenvolvimento"
	@echo "  make run-invoice-scheduler Executa o worker de invoice_scheduler em modo de desenvolvimento"
	@echo "  make docker-build         Constrói a imagem Docker"
	@echo "  make docker-run           Sobe os containers Docker"
	@echo "  make docker-stop          Para e remove os containers Docker"
	@echo "  make clean                Remove o ambiente virtual e arquivos temporários"
	@echo ""

# ------------------------------------
# create environment
# ------------------------------------
install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# ------------------------------------
# tests
# ------------------------------------
test: install
	$(PYTHON) -m pytest

# ------------------------------------
# cleaning
# ------------------------------------
clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# ------------------------------------
# local dev
# ------------------------------------
run-server:
	@echo "Iniciando servidor em modo de desenvolvimento..."
	$(PYTHON) -m uvicorn app.main:app --reload

run-invoice-worker:
	@echo "Iniciando worker invoice_issuer em modo de desenvolvimento..."
	$(PYTHON) -m app.workers.invoice_worker

run-invoice-scheduler:
	@echo "Iniciando worker invoice_scheduler em modo de desenvolvimento..."
	$(PYTHON) -m app.workers.invoice_scheduler

# ------------------------------------
# docker
# ------------------------------------
docker-build:
	@echo "Construindo imagem Docker..."
	docker compose build

docker-run:
	@echo "Subindo containers Docker..."
	docker compose up

docker-stop:
	@echo "Derrubando containers Docker..."
	docker compose down
