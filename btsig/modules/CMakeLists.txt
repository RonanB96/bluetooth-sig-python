cmake_minimum_required(VERSION 3.24)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    set(CMAKE_C_STANDARD 11)
    set(CMAKE_C_STANDARD_REQUIRED ON)
    set(CMAKE_C_EXTENSIONS OFF)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
    if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
        set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
    endif()
    project(btsig_characteristics LANGUAGES C)
endif()

add_library(btsig_warnings INTERFACE)
add_library(btsig::warnings ALIAS btsig_warnings)
target_compile_options(btsig_warnings INTERFACE
    -Wall -Wextra -Wpedantic -Werror -Wshadow -Wundef)

add_library(btsig_types INTERFACE)
add_library(btsig::types ALIAS btsig_types)
target_include_directories(btsig_types INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/types/include")

add_library(btsig_schema INTERFACE)
add_library(btsig::schema ALIAS btsig_schema)
target_include_directories(btsig_schema INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/schema/include")
target_link_libraries(btsig_schema INTERFACE btsig::types)

add_library(btsig_wire STATIC
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/word.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/medfloat.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/ieee754.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/real.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/utf8.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/wire/src/subbyte.c")
add_library(btsig::wire ALIAS btsig_wire)
set_target_properties(btsig_wire PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED ON C_EXTENSIONS OFF)
target_include_directories(btsig_wire PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/wire/include")
target_link_libraries(btsig_wire PUBLIC btsig::schema PRIVATE btsig::warnings m)

add_library(btsig_codec STATIC "${CMAKE_CURRENT_SOURCE_DIR}/codec/src/codec.c")
add_library(btsig::codec ALIAS btsig_codec)
set_target_properties(btsig_codec PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED ON C_EXTENSIONS OFF)
target_include_directories(btsig_codec PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/codec/include")
target_include_directories(btsig_codec PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/wire/src")
target_link_libraries(btsig_codec PUBLIC btsig::schema PRIVATE btsig::wire btsig::warnings m)

file(GLOB btsig_generated_sources CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/../generated/*/src/*.c")
file(GLOB btsig_override_sources CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/../override/*/src/*.c")
set(btsig_override_names "")
foreach(source IN LISTS btsig_override_sources)
    cmake_path(GET source PARENT_PATH source_dir)
    cmake_path(GET source_dir PARENT_PATH characteristic_dir)
    cmake_path(GET characteristic_dir FILENAME characteristic_name)
    list(APPEND btsig_override_names "${characteristic_name}")
endforeach()
# A handwritten codec in btsig/override replaces the generated codec of the same directory name.
set(btsig_characteristic_sources "")
foreach(source IN LISTS btsig_generated_sources)
    cmake_path(GET source PARENT_PATH source_dir)
    cmake_path(GET source_dir PARENT_PATH characteristic_dir)
    cmake_path(GET characteristic_dir FILENAME characteristic_name)
    if(characteristic_name IN_LIST btsig_override_names)
        continue()
    endif()
    list(APPEND btsig_characteristic_sources "${source}")
endforeach()
list(APPEND btsig_characteristic_sources ${btsig_override_sources})
if(NOT btsig_characteristic_sources)
    message(FATAL_ERROR
        "No generated characteristics in btsig/generated. "
        "Run `python -m tools.gss_ir.generate tools/gss_ir/characteristics.json` "
        "and `python -m tools.gss_ir.emit_cpp tools/gss_ir/characteristics.json`. "
        "characteristics.json is the blacklist.")
endif()
add_library(btsig_characteristics STATIC ${btsig_characteristic_sources})
add_library(btsig::characteristics ALIAS btsig_characteristics)
set_target_properties(btsig_characteristics PROPERTIES C_STANDARD 11 C_STANDARD_REQUIRED ON C_EXTENSIONS OFF)
target_link_libraries(btsig_characteristics PUBLIC btsig::types btsig::codec PRIVATE btsig::warnings)
foreach(source IN LISTS btsig_characteristic_sources)
    cmake_path(GET source PARENT_PATH source_dir)
    cmake_path(GET source_dir PARENT_PATH characteristic_dir)
    target_include_directories(btsig_characteristics PUBLIC "${characteristic_dir}/include")
endforeach()
