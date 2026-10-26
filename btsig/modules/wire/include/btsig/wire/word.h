#ifndef BTSIG_WIRE_WORD_H
#define BTSIG_WIRE_WORD_H

#include "btsig/schema/descriptor.h"
#include "btsig/types/status.h"

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Octet width of one wire value. Zero means the enumerator is not a known width.
size_t btsig_wire_width(uint8_t wire);

// Little-endian word in `data` (Core Specification 6.3, Volume 1, Part E, Section 2.9).
// BTSIG_INVALID_ARGUMENT when the buffer is shorter than the width, the width is unknown or above 8, or a
// pointer is null.
// BTSIG_OUT_OF_RANGE when an unsigned word does not fit in int64_t. Section 2.9.1 gives uint64
// the range 0 to 2^64-1, which this return type cannot hold.
btsig_error btsig_wire_read(const uint8_t* data, size_t size, uint8_t wire, int64_t* raw);

// Little-endian write of the low octets (Core Specification 6.3, Volume 1, Part E, Section 2.9).
// `out_size` is the octet width.
// BTSIG_INVALID_ARGUMENT when the pointer is null, the size is zero, or the size is wider than 8 octets.
btsig_error btsig_wire_write(uint8_t* out, size_t out_size, int64_t raw);

// True for medfloat16, medfloat32, and IEEE-754 binary32.
bool btsig_wire_is_real(uint8_t wire);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_WORD_H
