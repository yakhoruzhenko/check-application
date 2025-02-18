clean: ## clean
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -f .coverage

down: ## down
	docker compose down

down-v: ## down and remove all existing volumes
	docker compose down -v

up: ## up
	docker compose up -d check-app

lint: ## lint
	docker compose run --rm check-app-test-base sh -c " \
		flake8 . && \
		isort --check --diff . && \
		mypy ." && \
		yamllint .

sec: ## runs security tests
	docker compose run --rm check-app-test-base bandit .

test: ## test
	docker compose run --rm check-app-test

coverage: ## coverage
	docker compose run --rm check-app-test sh -c " \
		coverage run -m pytest && \
		coverage report -m "

seed: ## spins up the local app in the detached mode and seeds the dummy data into the DB
	docker compose up -d check-app
	for i in {1..10}; do \
		container_state=$$(docker container inspect -f '{{.State.Running}}' check-app); \
		echo "Container state: $$container_state"; \
		if [ "$$container_state" = "true" ]; then \
			echo "Container is running, executing script..."; \
			docker compose exec check-app python3 utils/populate.py; \
			break; \
		else \
			echo "Container is not running... waiting..."; \
			sleep 1; \
		fi \
	done

erd: ## creates ERD of the DB
	docker compose run --rm check-app-erd

.PHONY: docs  # to enforce always run mode
docs: ## build RTD content
	rm -rf docs && cd docs_builder && rm -rf _build && make html
	mkdir docs && mv docs_builder/_build/html/* docs && rm -rf docs_builder/_build
	touch docs/.nojekyll

# Absolutely awesome: https://marmelab.com/check/2016/02/29/auto-documented-makefile.html
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
