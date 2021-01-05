TEX = pandoc
src = *.yml
FLAGS = --pdf-engine=xelatex

output.pdf : $(src)
	$(TEX) $< -o $@ --template=template.tex $(FLAGS)
.PHONY: clean
clean :
	rm output.pdf
