#ifndef BTSIG_SCHEMA_DESCRIPTOR_H
#define BTSIG_SCHEMA_DESCRIPTOR_H

#include "btsig/types/status.h"

#include <stddef.h>
#include <stdint.h>

#define BTSIG_SCHEMA_VERSION 1

// Stored in a name or unit offset when that string is absent.
#define BTSIG_NO_TEXT ((uint16_t)0xFFFF)

enum {
    BTSIG_WIRE_UINT8 = 0,
    BTSIG_WIRE_UINT16,
    BTSIG_WIRE_UINT24,
    BTSIG_WIRE_UINT32,
    BTSIG_WIRE_UINT48,
    BTSIG_WIRE_UINT64,
    BTSIG_WIRE_SINT8,
    BTSIG_WIRE_SINT16,
    BTSIG_WIRE_SINT24,
    BTSIG_WIRE_SINT32,
    BTSIG_WIRE_BOOLEAN8,
    BTSIG_WIRE_BOOLEAN16,
    BTSIG_WIRE_BOOLEAN24,
    BTSIG_WIRE_BOOLEAN32,
    BTSIG_WIRE_MEDFLOAT16,
    BTSIG_WIRE_MEDFLOAT32,
    BTSIG_WIRE_FLOAT32,
    BTSIG_WIRE_UTF8,
    BTSIG_WIRE_UINT1,
    BTSIG_WIRE_UINT2,
};

enum {
    BTSIG_SENTINEL_NOT_KNOWN = 0,
    BTSIG_SENTINEL_NOT_VALID = 1,
};

typedef struct btsig_sentinel {
    int64_t raw_value;
    uint8_t meaning;
} btsig_sentinel;

// No pointers. A field table can stay in flash. Strings, sentinels, and allowed
// values are addressed from the characteristic descriptor that owns this field.
typedef struct btsig_field_descriptor {
    int64_t raw_minimum;
    int64_t raw_maximum;
    // Bits that may be set on a flags member. Zero for every other field.
    uint64_t flag_mask;
    uint16_t name_offset;
    uint16_t unit_offset;
    uint16_t offset;
    uint16_t sentinel_offset;
    uint16_t sentinel_count;
    uint16_t allowed_offset;
    uint16_t allowed_count;
    // Octet maximum of a utf8 member. Zero for every other wire type.
    // The member starts at `offset`: uint16_t size, then uint8_t data[utf8_capacity].
    uint16_t utf8_capacity;
    uint16_t unit_uuid;
    btsig_value_kind value_kind;
    uint8_t wire;
    int8_t coefficient;
    int8_t decimal_exponent;
    int8_t binary_exponent;
} btsig_field_descriptor;

typedef struct btsig_characteristic_descriptor {
    const char* text;
    const btsig_sentinel* sentinels;
    const int64_t* allowed;
    const btsig_field_descriptor* fields;
    uint16_t name_offset;
    uint16_t id_offset;
    uint16_t unit_offset;
    uint16_t uuid;
    uint16_t size;
    uint16_t field_count;
    uint8_t is_bitfield;
} btsig_characteristic_descriptor;

#endif
