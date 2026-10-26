#include "btsig/wire/subbyte.h"

#include "btsig/schema/descriptor.h"

#include <stdbool.h>

static bool covers(size_t size, size_t bit_offset, size_t width) {
    if (width < BTSIG_WIRE_MIN_SUBBYTE_BITS || width > BTSIG_WIRE_MAX_SUBBYTE_BITS) {
        return false;
    }
    const size_t last = bit_offset + width - 1U;
    return size > last / BTSIG_WIRE_BITS_PER_OCTET;
}

size_t btsig_wire_bit_width(uint8_t wire) {
    if (wire == BTSIG_WIRE_UINT1) {
        return BTSIG_WIRE_UINT1_BITS;
    }
    if (wire == BTSIG_WIRE_UINT2) {
        return BTSIG_WIRE_UINT2_BITS;
    }
    return 0;
}

btsig_error btsig_wire_read_bits(const uint8_t* data, size_t size, size_t bit_offset, size_t width, int64_t* raw) {
    btsig_error error = {0};
    if (raw == NULL || data == NULL || !covers(size, bit_offset, width)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    uint64_t value = 0;
    for (size_t bit = 0; bit < width; ++bit) {
        const size_t index = bit_offset + bit;
        const uint8_t byte = data[index / BTSIG_WIRE_BITS_PER_OCTET];
        if ((byte & (uint8_t)(1U << (index % BTSIG_WIRE_BITS_PER_OCTET))) != 0) {
            value |= (uint64_t)1 << bit;
        }
    }
    *raw = (int64_t)value;
    return error;
}

btsig_error btsig_wire_write_bits(uint8_t* out, size_t out_size, size_t bit_offset, size_t width, int64_t raw) {
    btsig_error error = {0};
    if (out == NULL || !covers(out_size, bit_offset, width)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    const int64_t limit = (int64_t)1 << width;
    if (raw < 0 || raw >= limit) {
        error.status = BTSIG_OUT_OF_RANGE;
        return error;
    }
    for (size_t bit = 0; bit < width; ++bit) {
        if ((raw & ((int64_t)1 << bit)) == 0) {
            continue;
        }
        const size_t index = bit_offset + bit;
        out[index / BTSIG_WIRE_BITS_PER_OCTET] =
            (uint8_t)(out[index / BTSIG_WIRE_BITS_PER_OCTET] | (uint8_t)(1U << (index % BTSIG_WIRE_BITS_PER_OCTET)));
    }
    return error;
}
