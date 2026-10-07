PAPER_MODE ?= draft

.PHONY: registry tables figures validate build bundle check clean verify-public

registry:
	python3 scripts/paper/build_results_registry.py

tables:
	python3 scripts/paper/generate_tables.py

figures:
	python3 scripts/paper/generate_figures.py

validate:
	PAPER_MODE=$(PAPER_MODE) python3 scripts/paper/validate_claims.py

build: registry tables figures validate
	cd paper && latexmk -pdf -halt-on-error -interaction=nonstopmode main.tex

bundle: build
	python3 scripts/paper/build_arxiv_bundle.py
	python3 scripts/paper/check_arxiv_bundle.py

check:
	python3 scripts/paper/check_arxiv_bundle.py
	PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ -q -p no:cacheprovider

clean:
	cd paper && latexmk -C

verify-public:
	PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_public_repository_hygiene.py tests/test_paper_render_hygiene.py -q -p no:cacheprovider
