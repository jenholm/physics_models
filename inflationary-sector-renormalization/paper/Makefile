TEX=main.tex
OUT=build
PDF=inflationary-sector-renormalization.pdf

all:
	mkdir -p $(OUT)
	mkdir -p $(OUT)/bib
	cp bib/references.bib $(OUT)/bib/
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(OUT) $(TEX)
	cd $(OUT) && bibtex main
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(OUT) $(TEX)
	cd $(OUT) && bibtex main
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(OUT) $(TEX)
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(OUT) $(TEX)
	cp $(OUT)/main.pdf $(PDF)

clean:
	rm -rf $(OUT)/*

.PHONY: all clean
