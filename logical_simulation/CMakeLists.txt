project(VehicleLogicalView)
cmake_minimum_required(VERSION 3.20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Include the Omnet++ specific CMake files, add Omnet++ to the Path etc.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(OmnetPP 6.0.1 EXACT REQUIRED)
include(OmnetppHelpers)

# Define a CMake Executable containing the source files for the Logical view simulation
add_executable(VehicleLogicalView
    src/DataDictionary.cpp
    src/DataDictionary.hpp
    src/Runnable.cpp
    src/Runnable.hpp
)
# Link the relevant Omnet++ libraries to the executable, OmnetPP::qtenv is the graphical environment
# replace it with OmnetPP::cmdenv for a CLI based interface that allows automatically running various
# simulations with different seeds.
# target_link_libraries(VehicleLogicalView PRIVATE OmnetPP::sim OmnetPP::qtenv OmnetPP::main OmnetPP::envir)
target_link_libraries(VehicleLogicalView PRIVATE OmnetPP::sim OmnetPP::qtenv OmnetPP::main OmnetPP::envir)
# Link the address and undefined behaviour sanitizers for easy of debugging programming errors
target_compile_options(VehicleLogicalView PRIVATE -fsanitize=address,undefined)
target_link_libraries(VehicleLogicalView PRIVATE -fsanitize=address,undefined)
# Tell CMake where to search the network description (ned) files and specify to use ISO C++17
set_target_properties(VehicleLogicalView PROPERTIES
    NED_FOLDERS "${CMAKE_CURRENT_SOURCE_DIR}/ned"
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Create a target for generating the simulation network
find_package(Python3)
add_custom_target(simnetwork ALL
    ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/GenerateSimulation.py 
        ${CMAKE_CURRENT_SOURCE_DIR}/vehicle_4.2.1_paldd.csv
        ${CMAKE_CURRENT_SOURCE_DIR}/central.definitions
    BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/sim.ned
)

add_dependencies(VehicleLogicalView simnetwork)