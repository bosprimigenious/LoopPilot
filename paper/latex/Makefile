# LoopPilot paper — arXiv-friendly build
# Template basis: standard article class (arXiv submit_latex guidelines)
# https://arxiv.org/help/submit_latex

MAIN = main
LATEX = pdflatex
BIBTEX = bibtex

.PHONY: all clean watch

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex references.bib
	$(LATEX) -interaction=nonstopmode $(MAIN)
	-$(BIBTEX) $(MAIN)
	$(LATEX) -interaction=nonstopmode $(MAIN)
	$(LATEX) -interaction=nonstopmode $(MAIN)

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.pdf

watch:
	@echo "Run 'make' after editing $(MAIN).tex"
