.PHONY: dev frontend test test-unit test-integration lint eval eval-all build up down generate-testset

dev:
	uvicorn src.api.main:app --reload --port 8000

frontend:
	streamlit run frontend/app.py --server.port 8501

test:
	pytest tests/unit/ tests/integration/ -v --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short --cov=src/rag --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v --tb=short

lint:
	ruff check src/ tests/
	mypy src/ --ignore-missing-imports

eval:
	python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml

eval-all:
	python -m src.eval.run_eval --config configs/eval_experiment_v1.yaml
	python -m src.eval.run_eval --config configs/eval_experiment_v2.yaml
	python -m src.eval.run_eval --config configs/eval_experiment_v3.yaml

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

generate-testset:
	python -m src.eval.testset_generator
