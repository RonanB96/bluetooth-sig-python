#ifndef BTSIG_WIRE_SUBBYTE_H
#define BTSIG_WIRE_SUBBYTE_H

#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

#define BTSIG_WIRE_BITS_PER_OCTET 8
#define BTSIG_WIRE_UINT1_BITS 1
#define BTSIG_WIRE_UINT2_BITS 2
#define BTSIG_WIRE_MIN_SUBBYTE_BITS BTSIG_WIRE_UINT1_BITS
#define BTSIG_WIRE_MAX_SUBBYTE_BITS (BTSIG_WIRE_BITS_PER_OCTET - 1)

// Bit width of uint1 or uint2. Zero for every other wire type.
size_t btsig_wire_bit_width(uint8_t wire);

// Read `width` bits starting at `bit_offset`. Bit 0 is the least significant bit of the first octet.
// BTSIG_INVALID_ARGUMENT when the buffer does not cover the bits, a pointer is null, or `width` is outside
// BTSIG_WIRE_MIN_SUBBYTE_BITS..BTSIG_WIRE_MAX_SUBBYTE_BITS.
btsig_error btsig_wire_read_bits(const uint8_t* data, size_t size, size_t bit_offset, size_t width, int64_t* raw);

// Write the low `width` bits of `raw` at `bit_offset`.
// BTSIG_INVALID_ARGUMENT when the buffer does not cover the bits, `out` is null, or `width` is outside
// BTSIG_WIRE_MIN_SUBBYTE_BITS..BTSIG_WIRE_MAX_SUBBYTE_BITS.
// BTSIG_OUT_OF_RANGE when `raw` is negative or does not fit in `width` bits.
btsig_error btsig_wire_write_bits(uint8_t* out, size_t out_size, size_t bit_offset, size_t width, int64_t raw);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_SUBBYTE_H
