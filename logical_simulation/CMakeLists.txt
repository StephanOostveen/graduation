project(ExteriorLightingLogicalView)
cmake_minimum_required(VERSION 3.20)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Include the Omnet++ specific CMake files, add Omnet++ to the Path etc.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(OmnetPP 5.5.1 EXACT REQUIRED)
include(OmnetppHelpers)

# Define a CMake Executable containing the source files for the Logical view simulation
add_executable(ExteriorLightingLogicalView
    src/DataDictionary.cpp
    src/DataDictionary.hpp
    src/Runnable.cpp
    src/Runnable.hpp
)
# Link the relevant Omnet++ libraries to the executable, OmnetPP::qtenv is the graphical environment
# replace it with OmnetPP::cmdenv for a CLI based interface that allows automatically running various
# simulations with different seeds.
# target_link_libraries(ExteriorLightingLogicalView PRIVATE OmnetPP::sim OmnetPP::qtenv OmnetPP::main OmnetPP::envir)
target_link_libraries(ExteriorLightingLogicalView PRIVATE OmnetPP::sim OmnetPP::qtenv OmnetPP::main OmnetPP::envir)
# Link the address and undefined behaviour sanitizers for easy of debugging programming errors
target_compile_options(ExteriorLightingLogicalView PRIVATE -fsanitize=address,undefined)
target_link_libraries(ExteriorLightingLogicalView PRIVATE -fsanitize=address,undefined)
# Tell CMake where to search the network description (ned) files and specify to use ISO C++17
set_target_properties(ExteriorLightingLogicalView PROPERTIES
    NED_FOLDERS "${CMAKE_CURRENT_SOURCE_DIR}/ned"
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)