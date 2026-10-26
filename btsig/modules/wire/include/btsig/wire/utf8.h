#ifndef BTSIG_WIRE_UTF8_H
#define BTSIG_WIRE_UTF8_H

#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

// BTSIG_INVALID_ARGUMENT when `data` is not well-formed UTF-8, or `data` is null with a non-zero size.
btsig_status btsig_wire_check_utf8(const uint8_t* data, size_t size);

// Copy a well-formed UTF-8 value into `destination`.
// BTSIG_INVALID_ARGUMENT when `copied` is null, `data` is not well-formed UTF-8, or a pointer is null with a
// non-zero size.
// BTSIG_LENGTH_MISMATCH when `size` is greater than `destination_size`.
// On success, `*copied` is the octet count copied.
btsig_error btsig_wire_read_utf8(const uint8_t* data, size_t size, uint8_t* destination, size_t destination_size,
                                 size_t* copied);

// Copy `data` to `out` when `data` is well-formed UTF-8 and fits.
// BTSIG_INVALID_ARGUMENT when `data` is not well-formed UTF-8, or a pointer is null with a non-zero size.
// BTSIG_LENGTH_MISMATCH when `size` is greater than `out_size`.
// Only `status` is set on the returned error.
btsig_error btsig_wire_write_utf8(const uint8_t* data, size_t size, uint8_t* out, size_t out_size);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_UTF8_H
