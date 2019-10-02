TEX = pandoc
src = *.yml
FLAGS = --latex-engine=xelatex

output.pdf : $(src)
	$(TEX) $< -o $@ --template=template.tex $(FLAGS)
.PHONY: clean
clean :
	rm output.pdf

