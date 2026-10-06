PAPER_MODE ?= draft

.PHONY: registry tables figures validate build bundle check replay clean manifest b2tables

registry:
	python scripts/paper/build_results_registry.py

manifest:
	python scripts/paper/build_b2_evidence_manifest.py

tables:
	python scripts/paper/generate_tables.py

b2tables:
	python scripts/paper/generate_b2_tables.py

figures:
	python scripts/paper/generate_figures.py

validate:
	PAPER_MODE=$(PAPER_MODE) python scripts/paper/validate_claims.py

replay:
	python scripts/paper/replay_m24d_reference.py

build: registry manifest tables b2tables figures validate
	cd paper && latexmk -pdf -halt-on-error -interaction=nonstopmode main.tex

bundle: build
	python scripts/paper/build_arxiv_bundle.py
	python scripts/paper/check_arxiv_bundle.py

clean:
	cd paper && latexmk -C
