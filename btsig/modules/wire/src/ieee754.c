#include "ieee754.h"

#include <stdint.h>
#include <string.h>

static float binary32_from_bits(uint32_t bits) {
    float value = 0.0f;
    memcpy(&value, &bits, sizeof value);
    return value;
}

static uint32_t bits_from_binary32(float value) {
    uint32_t bits = 0;
    memcpy(&bits, &value, sizeof bits);
    return bits;
}

btsig_error btsig_wire_decode_binary32(int64_t raw, double* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    *value = (double)binary32_from_bits((uint32_t)raw);
    btsig_error ok = {0};
    return ok;
}

btsig_error btsig_wire_encode_binary32(double value, int64_t* raw) {
    if (raw == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    *raw = (int64_t)bits_from_binary32((float)value);
    btsig_error ok = {0};
    return ok;
}
