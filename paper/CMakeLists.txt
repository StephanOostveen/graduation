cmake_minimum_required(VERSION 3.22)

project(paper NONE)
include(UseLATEX/UseLATEX.cmake)

add_latex_document(main.tex
    IMAGE_DIRS images
    INPUTS
        titlepage.tex
        1.0.introduction.tex
        2.0.domain.tex
        2.1.architectures.tex
        2.2.real-time-comm.tex
        2.3.tsn.tex
        2.4.can.tex
        3.0.problem_statement.tex
        4.0.sota_analysis.tex
        5.0.research_description.tex
        5.1.research_question.tex
        5.2.research_contribution.tex
        6.0.approach.tex
        6.1.embedded_system.tex
        6.1.1.in_vehicle_network.tex
        6.1.2.programmable_end_nodes.tex
        6.2.modelling_network.tex
        6.3.model_generation.tex
        7.0.results.tex
        8.0.discussion.tex
        9.0.conclusion.tex
        10.0.reflection.tex
        A.tsn.tex
        network_overview_table.tex
        network_overview_figure.tex
        rtos_tasks.tex
        sample.tikzstyles
        figures/logical_example.tikz
        figures/deployment_example.tikz
    BIBFILES resources.bib USE_BIBLATEX
)