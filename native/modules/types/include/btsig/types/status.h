#pragma once

#include <stddef.h>
#include <stdint.h>

typedef enum btsig_status {
    BTSIG_OK = 0,
    BTSIG_INSUFFICIENT_DATA = 1,
    BTSIG_LENGTH_MISMATCH = 2,
    BTSIG_UNKNOWN_UUID = 3,
    BTSIG_OUT_OF_RANGE = 4,
    BTSIG_BUFFER_TOO_SMALL = 5,
    BTSIG_INVALID_ARGUMENT = 6,
    BTSIG_NOT_KNOWN = 7,
    BTSIG_NOT_VALID = 8
} btsig_status;

typedef enum btsig_value_kind {
    BTSIG_VALUE_UINT8,
    BTSIG_VALUE_UINT16,
    BTSIG_VALUE_UINT32,
    BTSIG_VALUE_UINT64,
    BTSIG_VALUE_SINT8,
    BTSIG_VALUE_SINT16,
    BTSIG_VALUE_SINT32,
    BTSIG_VALUE_DOUBLE
} btsig_value_kind;

typedef struct btsig_bytes {
    const uint8_t* data;
    size_t size;
} btsig_bytes;

typedef struct btsig_characteristic btsig_characteristic;
typedef struct btsig_context btsig_context;

typedef struct btsig_error {
    btsig_status status;
    const btsig_characteristic* characteristic;
    const char* field;
    btsig_bytes bytes;
} btsig_error;
