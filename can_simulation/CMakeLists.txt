cmake_minimum_required(VERSION 3.20)
project(CANSimulation)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Include the Omnet++ specific CMake files, add Omnet++ to the Path etc.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/omnetpp-cmake")
find_package(OmnetPP 6.0.1 EXACT REQUIRED)
include(OmnetppHelpers)
include(CompilerWarnings)

add_library(project_warnings INTERFACE)
set_project_warnings(project_warnings)

add_library(FiCo4OMNeT SHARED 
    FiCo4OMNeT/src/fico4omnet/applications/can/sink/CanTrafficSinkAppBase.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/sink/CanTrafficSinkAppBase.h
    FiCo4OMNeT/src/fico4omnet/applications/can/source/CanTrafficSourceAppBase.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/source/CanTrafficSourceAppBase.h
    FiCo4OMNeT/src/fico4omnet/applications/can/source/CanTrafficSourceAppBaseStoppable.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/source/CanTrafficSourceAppBaseStoppable.h
    FiCo4OMNeT/src/fico4omnet/applications/can/source/colouredsourceapp/CanColouredSourceApp.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/source/colouredsourceapp/CanColouredSourceApp.h
    FiCo4OMNeT/src/fico4omnet/applications/flexray/sink/FRTrafficSinkAppBase.cc
    FiCo4OMNeT/src/fico4omnet/applications/flexray/sink/FRTrafficSinkAppBase.h
    FiCo4OMNeT/src/fico4omnet/applications/flexray/source/FRTrafficSourceAppBase.cc
    FiCo4OMNeT/src/fico4omnet/applications/flexray/source/FRTrafficSourceAppBase.h
    FiCo4OMNeT/src/fico4omnet/base/FiCo4OMNeT_Defs.h
    FiCo4OMNeT/src/fico4omnet/buffer/Buffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/Buffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanBuffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanInputBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanInputBuffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanOutputBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/can/CanOutputBuffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FRBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FRBuffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FRInputBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FRInputBuffer.h
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FROutputBuffer.cc
    FiCo4OMNeT/src/fico4omnet/buffer/flexray/FROutputBuffer.h
    FiCo4OMNeT/src/fico4omnet/bus/BusPort.cc
    FiCo4OMNeT/src/fico4omnet/bus/BusPort.h
    FiCo4OMNeT/src/fico4omnet/bus/can/CanBusLogic.cc
    FiCo4OMNeT/src/fico4omnet/bus/can/CanBusLogic.h
    FiCo4OMNeT/src/fico4omnet/bus/can/CanID.cc
    FiCo4OMNeT/src/fico4omnet/bus/can/CanID.h
    FiCo4OMNeT/src/fico4omnet/bus/flexray/FRBusLogic.cc
    FiCo4OMNeT/src/fico4omnet/bus/flexray/FRBusLogic.h
    FiCo4OMNeT/src/fico4omnet/bus/flexray/FRTopologyPort.cc
    FiCo4OMNeT/src/fico4omnet/bus/flexray/FRTopologyPort.h
    FiCo4OMNeT/src/fico4omnet/linklayer/NodePort.cc
    FiCo4OMNeT/src/fico4omnet/linklayer/NodePort.h
    FiCo4OMNeT/src/fico4omnet/linklayer/can/CanPortInput.cc
    FiCo4OMNeT/src/fico4omnet/linklayer/can/CanPortInput.h
    FiCo4OMNeT/src/fico4omnet/linklayer/can/CanPortOutput.cc
    FiCo4OMNeT/src/fico4omnet/linklayer/can/CanPortOutput.h
    FiCo4OMNeT/src/fico4omnet/linklayer/flexray/FRPortInput.cc
    FiCo4OMNeT/src/fico4omnet/linklayer/flexray/FRPortInput.h
    FiCo4OMNeT/src/fico4omnet/linklayer/flexray/FRPortOutput.cc
    FiCo4OMNeT/src/fico4omnet/linklayer/flexray/FRPortOutput.h
    FiCo4OMNeT/src/fico4omnet/scheduler/can/CanClock.cc
    FiCo4OMNeT/src/fico4omnet/scheduler/can/CanClock.h
    FiCo4OMNeT/src/fico4omnet/scheduler/flexray/FRScheduler.cc
    FiCo4OMNeT/src/fico4omnet/scheduler/flexray/FRScheduler.h
    FiCo4OMNeT/src/fico4omnet/scheduler/flexray/SchedulerEvent.cc
    FiCo4OMNeT/src/fico4omnet/scheduler/flexray/SchedulerEvent.h
    FiCo4OMNeT/src/fico4omnet/synchronisation/flexray/FRSync.cc
    FiCo4OMNeT/src/fico4omnet/synchronisation/flexray/FRSync.h
    FiCo4OMNeT/src/fico4omnet/utilities/HelperFunctions.cc
    FiCo4OMNeT/src/fico4omnet/utilities/HelperFunctions.h
    FiCo4OMNeT/src/fico4omnet/utilities/ResultFilters.cc
    FiCo4OMNeT/src/fico4omnet/utilities/ResultFilters.h

    FiCo4OMNeT/src/fico4omnet/applications/can/sink/lysinkapp/CanLySinkApp.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/sink/lysinkapp/CanLySinkApp.h
    FiCo4OMNeT/src/fico4omnet/applications/can/source/lysourceapp/CanLySourceApp.cc
    FiCo4OMNeT/src/fico4omnet/applications/can/source/lysourceapp/CanLySourceApp.h
    
    FiCo4OMNeT/src/fico4omnet/operatingsystem/Logical.cc
    FiCo4OMNeT/src/fico4omnet/operatingsystem/Logical.h

    FiCo4OMNeT/src/fico4omnet/operatingsystem/Scheduler.cc
    FiCo4OMNeT/src/fico4omnet/operatingsystem/Scheduler.h

    FiCo4OMNeT/src/fico4omnet/operatingsystem/DataDictionary.cc
    FiCo4OMNeT/src/fico4omnet/operatingsystem/DataDictionary.h
)

add_custom_command(TARGET FiCo4OMNeT PRE_BUILD
                    COMMAND opp_featuretool defines > src/fico4omnet/features.h
                    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/FiCo4OMNeT
                    BYPRODUCTS src/fico4omnet/features.h
                    VERBATIM
)

target_compile_definitions(FiCo4OMNeT PUBLIC -DWITH_CAN_COMMON -DWITH_FR_COMMON)
target_include_directories(FiCo4OMNeT PUBLIC 
    FiCo4OMNeT/src
    FiCo4OMNeT/src/fico4omnet/applications/can/source
    FiCo4OMNeT/src/fico4omnet/applications/can/source/lysourceapp
    FiCo4OMNeT/src/fico4omnet/applications/can/sink
    FiCo4OMNeT/src/fico4omnet/applications/can/sink/lysinkapp
    FiCo4OMNeT/src/fico4omnet/base
    FiCo4OMNeT/src/fico4omnet/buffer
    FiCo4OMNeT/src/fico4omnet/buffer/can
    FiCo4OMNeT/src/fico4omnet/bus
    FiCo4OMNeT/src/fico4omnet/bus/can
    FiCo4OMNeT/src/fico4omnet/linklayer
    FiCo4OMNeT/src/fico4omnet/linklayer/can
    FiCo4OMNeT/src/fico4omnet/operatingsystem
    FiCo4OMNeT/src/fico4omnet/scheduler/can/
    FiCo4OMNeT/src/fico4omnet/utilities/
)

generate_opp_message(FiCo4OMNeT/src/fico4omnet/linklayer/can/messages/CanDataFrame.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/linklayer/can/messages/ErrorFrame.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/linklayer/flexray/messages/FRFrame.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/scheduler/flexray/SchedulerMessage.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/scheduler/flexray/SchedulerMessageEvents.msg
    TARGET FiCo4OMNeT 
)

generate_opp_message(FiCo4OMNeT/src/fico4omnet/applications/can/sink/lysinkapp/FrameRequest.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/operatingsystem/CanList.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/operatingsystem/DataDictionaryDefinition.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/operatingsystem/DataDictionaryValue.msg
    TARGET FiCo4OMNeT 
)
generate_opp_message(FiCo4OMNeT/src/fico4omnet/operatingsystem/ScheduleMsg.msg
    TARGET FiCo4OMNeT 
)
# You will need to tweak and add the additional properties for your project
set_target_properties(FiCo4OMNeT PROPERTIES
    NED_FOLDERS FiCo4OMNeT/src/
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF    
)
target_link_libraries(FiCo4OMNeT PRIVATE  OmnetPP::main project_warnings)
target_compile_options(FiCo4OMNeT
                             PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
target_link_libraries(FiCo4OMNeT
                            PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
