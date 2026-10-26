#include "btsig/wire/word.h"

#include <stdbool.h>
#include <stdint.h>

static bool is_signed(uint8_t wire) {
    switch (wire) {
    case BTSIG_WIRE_SINT8:
    case BTSIG_WIRE_SINT16:
    case BTSIG_WIRE_SINT24:
    case BTSIG_WIRE_SINT32:
        return true;
    default:
        return false;
    }
}

size_t btsig_wire_width(uint8_t wire) {
    switch (wire) {
    case BTSIG_WIRE_UINT8:
    case BTSIG_WIRE_SINT8:
    case BTSIG_WIRE_BOOLEAN8:
        return 1;
    case BTSIG_WIRE_UINT16:
    case BTSIG_WIRE_SINT16:
    case BTSIG_WIRE_BOOLEAN16:
    case BTSIG_WIRE_MEDFLOAT16:
        return 2;
    case BTSIG_WIRE_UINT24:
    case BTSIG_WIRE_SINT24:
    case BTSIG_WIRE_BOOLEAN24:
        return 3;
    case BTSIG_WIRE_UINT32:
    case BTSIG_WIRE_SINT32:
    case BTSIG_WIRE_BOOLEAN32:
    case BTSIG_WIRE_MEDFLOAT32:
    case BTSIG_WIRE_FLOAT32:
        return 4;
    case BTSIG_WIRE_UINT48:
        return 6;
    case BTSIG_WIRE_UINT64:
        return 8;
    default:
        return 0;
    }
}

bool btsig_wire_is_real(uint8_t wire) {
    return wire == BTSIG_WIRE_MEDFLOAT16 || wire == BTSIG_WIRE_MEDFLOAT32 || wire == BTSIG_WIRE_FLOAT32;
}

btsig_error btsig_wire_read(const uint8_t* data, size_t size, uint8_t wire, int64_t* raw) {
    btsig_error error = {0};
    const size_t octets = btsig_wire_width(wire);
    // btsig_wire_width returns 0 for an unknown enumerator. bits_in_wire is uint32_t,
    // so a zero width wraps bits_in_wire - 1 before the sign-bit shift. A width
    // above 8 shifts a byte out of uint64_t.
    if (raw == NULL || octets == 0 || octets > sizeof(uint64_t) || data == NULL || size < octets) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    uint64_t bits = 0;
    for (size_t index = 0; index < octets; ++index) {
        const uint32_t shift = (uint32_t)index * 8U;
        bits |= (uint64_t)data[index] << shift;
    }
    if (!is_signed(wire)) {
        if (bits > (uint64_t)INT64_MAX) {
            error.status = BTSIG_OUT_OF_RANGE;
            return error;
        }
        *raw = (int64_t)bits;
        return error;
    }
    // Two's complement, sign bit most significant (Core Specification 6.3, Volume 1, Part E, Section 2.9.1).
    const uint32_t bits_in_wire = (uint32_t)(octets * 8U);
    if (bits_in_wire < 64U && (bits & ((uint64_t)1 << (bits_in_wire - 1U))) != 0U) {
        bits |= ~(((uint64_t)1 << bits_in_wire) - 1U);
    }
    *raw = (int64_t)bits;
    return error;
}

btsig_error btsig_wire_write(uint8_t* out, size_t out_size, int64_t raw) {
    btsig_error error = {0};
    // A shift of 64 bits or more is undefined for uint64_t.
    if (out == NULL || out_size == 0 || out_size > sizeof(uint64_t)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    const uint64_t bits = (uint64_t)raw;
    for (size_t index = 0; index < out_size; ++index) {
        const uint32_t shift = (uint32_t)index * 8U;
        out[index] = (uint8_t)(bits >> shift);
    }
    return error;
}
