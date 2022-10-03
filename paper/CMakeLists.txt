cmake_minimum_required(VERSION 3.22)

project(preparation_paper NONE)
include(UseLATEX/UseLATEX.cmake)
add_latex_document(main.tex
    INPUTS
        titlepage.tex
        1.0.introduction.tex
        2.0.problem_statement.tex
        3.0.sota_analysis.tex
        4.0.research_description.tex
        5.0.planning.tex
    BIBFILES resources.bib USE_BIBLATEX
    IMAGE_DIRS images
)