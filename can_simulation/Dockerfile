# Author: Stephan Oostveen, stephan_oostveen@hotmail.com
# Date: 19-03-2024

FROM ubuntu:jammy-20240227
SHELL ["/bin/bash", "-c"]
# Avoid hanging on tzdata input during apt install
ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install required packages
RUN apt-get update &&  apt-get install -y build-essential clang lld gdb bison flex perl \
python3 python3-pip qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \
libqt5opengl5-dev libxml2-dev zlib1g-dev doxygen graphviz \
libwebkit2gtk-4.0-37 xdg-utils python3-pandas python3-matplotlib python3-scipy \
python3-seaborn python3-numpy wget git cmake ninja-build

RUN python3 -m pip install --user --upgrade posix_ipc

# Download and install OMNeT++ 6.0.2
WORKDIR /home
RUN wget https://github.com/omnetpp/omnetpp/releases/download/omnetpp-6.0.2/omnetpp-6.0.2-linux-x86_64.tgz \
&& tar -xf omnetpp-6.0.2-linux-x86_64.tgz

WORKDIR /home/omnetpp-6.0.2

# Directory for 'installing' system menu icon, without this directory the make script fails
RUN mkdir /usr/share/desktop-directories/

# Set the environment and build OMNeT++
RUN . ./setenv && ./configure WITH_OSG=no && make -j8 

# Clone the graduation project repository containing the Omnet++ model, for efficiency don't clone 
# all submodules but only the ones needed for simulation
WORKDIR /home/project
COPY . /home/project/
# Build the modified Fico4OMNeT framework, for unknown reasons linking fails when using GCC,
# so compile using clang
WORKDIR /home/project/build
RUN . /home/omnetpp-6.0.2/setenv && CC=clang CXX=clang++ cmake -DCMAKE_BUILD_TYPE:STRING=Release \
../ -G Ninja && ninja

# OMNeT++ provides us with a graphical and commandline environment. The graphical 
# environment is helpfull for debugging but has lower simulation performance compared
# to the command line environment. The command line environment also provides parallel
# simulation where multiple simulations are performed in parallel (each simulation is
# still single threaded). These three methods all require a different invocation.
#
# Additionally our work defined two different experiments with the names: 
#`ModifiedBandwidth` and `RandomBitstuffing`, which must be passed to the commandline
# interface as an argument. Below we show the three different invocations


# Graphical invocation:
# opp_run -l build/libFiCo4OMNeT.so -n FiCo4OMNeT/examplesLy:FiCo4OMNeT/src/ FiCo4OMNeT/examplesLy/LYES/omnetpp.ini FiCo4OMNeT/examplesLy/LYES/executionTimes.ini

# Single threaded commandline of the `ModifiedBandwidth` experiment, executing all the runs:
# opp_run -u Cmdenv -c ModifiedBandwidth -l build/libFiCo4OMNeT.so -n FiCo4OMNeT/examplesLy:FiCo4OMNeT/src/ FiCo4OMNeT/examplesLy/LYES/omnetpp.ini FiCo4OMNeT/examplesLy/LYES/executionTimes.ini

# Multi threaded commandline of the `ModifiedBandwidth` experiment, executing all the runs:
# opp_runall ./build/LYSim -c ModifiedBandwidth -n FiCo4OMNeT/examplesLy:FiCo4OMNeT/src/ FiCo4OMNeT/examplesLy/LYES/omnetpp.ini FiCo4OMNeT/examplesLy/LYES/executionTimes.ini
WORKDIR /home/project
COPY <<EOF run.sh
    #!/bin/bash
    . /home/omnetpp-6.0.2/setenv
    opp_runall ./build/LYSim -c ModifiedBandwidth -n FiCo4OMNeT/examplesLy:FiCo4OMNeT/src/ FiCo4OMNeT/examplesLy/LYES/omnetpp.ini FiCo4OMNeT/examplesLy/LYES/executionTimes.ini
EOF
RUN chmod +x run.sh

CMD ["/bin/bash", "-c", "/home/project/run.sh"]