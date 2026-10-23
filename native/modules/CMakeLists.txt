cmake_minimum_required(VERSION 3.24)

project(btsig_characteristics LANGUAGES C CXX)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(btsig_types INTERFACE)
add_library(btsig::types ALIAS btsig_types)
target_include_directories(btsig_types INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/types/include")

add_library(btsig_schema INTERFACE)
add_library(btsig::schema ALIAS btsig_schema)
target_include_directories(btsig_schema INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/schema/include")
target_link_libraries(btsig_schema INTERFACE btsig::types)

add_library(btsig_codec STATIC "${CMAKE_CURRENT_SOURCE_DIR}/codec/src/codec.cpp")
add_library(btsig::codec ALIAS btsig_codec)
target_include_directories(btsig_codec PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/codec/include")
target_link_libraries(btsig_codec PUBLIC btsig::schema)
target_compile_options(btsig_codec PRIVATE -Wall -Wextra -Wpedantic)

file(GLOB btsig_characteristic_sources CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/../generated/*/src/*.cpp")
if(NOT btsig_characteristic_sources)
    message(FATAL_ERROR
        "No generated characteristics in native/generated. "
        "Run `python -m tools.gss_ir.generate tools/gss_ir/characteristics.json` "
        "and `python -m tools.gss_ir.emit_cpp tools/gss_ir/characteristics.json`.")
endif()
add_library(btsig_characteristics STATIC ${btsig_characteristic_sources})
add_library(btsig::characteristics ALIAS btsig_characteristics)
target_link_libraries(btsig_characteristics PUBLIC btsig::types PRIVATE btsig::codec)
target_compile_options(btsig_characteristics PRIVATE -Wall -Wextra -Wpedantic)
foreach(source IN LISTS btsig_characteristic_sources)
    cmake_path(GET source PARENT_PATH source_dir)
    cmake_path(GET source_dir PARENT_PATH characteristic_dir)
    target_include_directories(btsig_characteristics PUBLIC "${characteristic_dir}/include")
endforeach()

set(BTSIG_EXAMPLE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../examples/characteristic_api")

add_executable(characteristic_api_cpp "${BTSIG_EXAMPLE_DIR}/cpp/main.cpp")
target_link_libraries(characteristic_api_cpp PRIVATE btsig::characteristics)
target_compile_options(characteristic_api_cpp PRIVATE -Wall -Wextra -Wpedantic)

add_executable(characteristic_api_c "${BTSIG_EXAMPLE_DIR}/c/main.c")
target_link_libraries(characteristic_api_c PRIVATE btsig::characteristics)
set_target_properties(characteristic_api_c PROPERTIES LINKER_LANGUAGE CXX)
target_compile_options(characteristic_api_c PRIVATE -Wall -Wextra -Wpedantic)
