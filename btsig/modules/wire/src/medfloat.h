#ifndef BTSIG_WIRE_MEDFLOAT_H
#define BTSIG_WIRE_MEDFLOAT_H

#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

btsig_error btsig_wire_decode_medfloat16(int64_t raw, double* value);
btsig_error btsig_wire_encode_medfloat16(double value, int64_t* raw);
btsig_error btsig_wire_decode_medfloat32(int64_t raw, double* value);
btsig_error btsig_wire_encode_medfloat32(double value, int64_t* raw);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_WIRE_MEDFLOAT_H
