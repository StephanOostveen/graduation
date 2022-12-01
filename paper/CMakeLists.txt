cmake_minimum_required(VERSION 3.22)

project(preparation_paper NONE)
include(UseLATEX/UseLATEX.cmake)
add_latex_document(main.tex
    INPUTS
        titlepage.tex
        1.0.introduction.tex
        2.0.domain.tex
        3.0.problem_statement.tex
        4.0.sota_analysis.tex
        5.0.research_description.tex
        6.0.feasibility_experiments.tex
        6.1.in_vehicle_network.tex
        6.2.network_traffic.tex
        6.3.omnetpp.tex
        7.0.planning.tex
        sample.tikzstyles
        figures/logical_example.tikz
        figures/deployment_example.tikz
    BIBFILES resources.bib USE_BIBLATEX
    IMAGE_DIRS images
)