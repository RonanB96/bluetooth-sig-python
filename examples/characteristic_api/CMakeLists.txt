cmake_minimum_required(VERSION 3.24)

set(BTSIG_API "BOTH" CACHE STRING "Sample programs to build: C, CXX, or BOTH")
set_property(CACHE BTSIG_API PROPERTY STRINGS C CXX BOTH)
if(NOT BTSIG_API MATCHES "^(C|CXX|BOTH)$")
    message(FATAL_ERROR "BTSIG_API must be C, CXX, or BOTH, got '${BTSIG_API}'.")
endif()

set(BTSIG_SAMPLE_LANGUAGES CXX)
if(BTSIG_API STREQUAL "C" OR BTSIG_API STREQUAL "BOTH")
    list(PREPEND BTSIG_SAMPLE_LANGUAGES C)
    set(CMAKE_C_STANDARD 99)
    set(CMAKE_C_STANDARD_REQUIRED ON)
    set(CMAKE_C_EXTENSIONS OFF)
endif()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif()

project(btsig_characteristic_api LANGUAGES ${BTSIG_SAMPLE_LANGUAGES})

add_subdirectory(
    "${CMAKE_CURRENT_SOURCE_DIR}/../../btsig/modules"
    "${CMAKE_CURRENT_BINARY_DIR}/btsig"
)

if(BTSIG_API STREQUAL "CXX" OR BTSIG_API STREQUAL "BOTH")
    add_executable(characteristic_api_cpp cpp/main.cpp)
    target_link_libraries(characteristic_api_cpp PRIVATE btsig::characteristics btsig::warnings)
endif()

if(BTSIG_API STREQUAL "C" OR BTSIG_API STREQUAL "BOTH")
    add_executable(characteristic_api_c c/main.c)
    target_link_libraries(characteristic_api_c PRIVATE btsig::characteristics btsig::warnings)
    set_target_properties(characteristic_api_c PROPERTIES LINKER_LANGUAGE CXX)
endif()
