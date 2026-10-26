#ifndef BTSIG_WIRE_IEEE754_H
#define BTSIG_WIRE_IEEE754_H

#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

// IEEE 754 binary32 widened to double (Core Specification 6.3, Volume 1, Part E, Section 2.9.1).
btsig_error btsig_wire_decode_binary32(int64_t raw, double* value);
btsig_error btsig_wire_encode_binary32(double value, int64_t* raw);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_IEEE754_H
