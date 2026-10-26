#include "real.h"

#include "btsig/schema/descriptor.h"

#include "ieee754.h"
#include "medfloat.h"

btsig_error btsig_wire_decode_real(uint8_t wire, int64_t raw, double* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    if (wire == BTSIG_WIRE_MEDFLOAT16) {
        return btsig_wire_decode_medfloat16(raw, value);
    }
    if (wire == BTSIG_WIRE_MEDFLOAT32) {
        return btsig_wire_decode_medfloat32(raw, value);
    }
    if (wire == BTSIG_WIRE_FLOAT32) {
        return btsig_wire_decode_binary32(raw, value);
    }
    btsig_error invalid = {0};
    invalid.status = BTSIG_INVALID_ARGUMENT;
    return invalid;
}

btsig_error btsig_wire_encode_real(uint8_t wire, double value, int64_t* raw) {
    if (raw == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    if (wire == BTSIG_WIRE_MEDFLOAT16) {
        return btsig_wire_encode_medfloat16(value, raw);
    }
    if (wire == BTSIG_WIRE_MEDFLOAT32) {
        return btsig_wire_encode_medfloat32(value, raw);
    }
    if (wire == BTSIG_WIRE_FLOAT32) {
        return btsig_wire_encode_binary32(value, raw);
    }
    btsig_error invalid = {0};
    invalid.status = BTSIG_INVALID_ARGUMENT;
    return invalid;
}
