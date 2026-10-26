cmake_minimum_required(VERSION 3.24)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
endif()

project(btsig_characteristic_api LANGUAGES C)

add_subdirectory(
    "${CMAKE_CURRENT_SOURCE_DIR}/../../btsig/modules"
    "${CMAKE_CURRENT_BINARY_DIR}/btsig"
)

add_executable(characteristic_api_c c/main.c)
target_link_libraries(characteristic_api_c PRIVATE btsig::characteristics btsig::warnings)
