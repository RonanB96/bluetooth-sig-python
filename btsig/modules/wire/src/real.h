#ifndef BTSIG_WIRE_REAL_H
#define BTSIG_WIRE_REAL_H

#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

// BTSIG_OUT_OF_RANGE for medfloat NRes or reserved, or when a finite value packs as a medfloat special.
// BTSIG_INVALID_ARGUMENT when the out-pointer is null or the wire type is not real.
btsig_error btsig_wire_decode_real(uint8_t wire, int64_t raw, double* value);
btsig_error btsig_wire_encode_real(uint8_t wire, double value, int64_t* raw);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_REAL_H
