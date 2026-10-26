#include "medfloat.h"

#include <math.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct IntRange {
    int minimum;
    int maximum;
} IntRange;

// Exponent then mantissa, base 10. Specials are exact words, not products.
typedef struct DecimalFloat {
    int exponent_bits;
    int mantissa_bits;
    IntRange exponent;
    IntRange mantissa;
    int64_t positive_infinity;
    int64_t negative_infinity;
    int64_t nan;
    int64_t nres;
    int64_t reserved;
} DecimalFloat;

static int field_mask(int bits) {
    return (1 << bits) - 1;
}

static bool is_special(int64_t raw, const DecimalFloat* format) {
    return raw == format->positive_infinity || raw == format->negative_infinity || raw == format->nan ||
           raw == format->nres || raw == format->reserved;
}

// ISO/IEEE 11073-20601 SFLOAT-Type, Personal Health Devices Transcoding White Paper V15r00 §2.2.2.
static const DecimalFloat kSfloat = {
    .exponent_bits = 4,
    .mantissa_bits = 12,
    .exponent = {.minimum = -8, .maximum = 7},
    .mantissa = {.minimum = -2048, .maximum = 2047},
    .positive_infinity = 0x07FE,
    .negative_infinity = 0x0802,
    .nan = 0x07FF,
    .nres = 0x0800,
    .reserved = 0x0801,
};

// ISO/IEEE 11073-20601 FLOAT-Type, Personal Health Devices Transcoding White Paper V15r00 §2.2.1.
static const DecimalFloat kFloat = {
    .exponent_bits = 8,
    .mantissa_bits = 24,
    .exponent = {.minimum = -128, .maximum = 127},
    .mantissa = {.minimum = -8388608, .maximum = 8388607},
    .positive_infinity = 0x007FFFFE,
    .negative_infinity = 0x00800002,
    .nan = 0x007FFFFF,
    .nres = 0x00800000,
    .reserved = 0x00800001,
};

static const double decimal_radix = 10.0;

static double decade_power(int exponent) {
    double decade = 1.0;
    if (exponent >= 0) {
        for (int step = 0; step < exponent; ++step) {
            decade *= decimal_radix;
        }
        return decade;
    }
    for (int step = exponent; step < 0; ++step) {
        decade *= decimal_radix;
    }
    return 1.0 / decade;
}

static int sign_extend(int value, int bits) {
    const int sign = 1 << (bits - 1);
    if ((value & sign) != 0) {
        return value - (1 << bits);
    }
    return value;
}

static int twos_bits(int value, int bits) {
    if (value < 0) {
        return value + (1 << bits);
    }
    return value;
}

static double product(int mantissa, int exponent) {
    return (double)mantissa * decade_power(exponent);
}

typedef struct MantissaExponent {
    int mantissa;
    int exponent;
} MantissaExponent;

static btsig_error choose(double value, IntRange exponent_range, IntRange mantissa_range, MantissaExponent* chosen) {
    bool found = false;
    int best_mantissa = 0;
    int best_exponent = 0;
    double best_error = INFINITY;
    for (int exponent = exponent_range.minimum; exponent <= exponent_range.maximum; ++exponent) {
        const double potential = value * decade_power(-exponent);
        const int mantissa = (int)llround(potential);
        if (mantissa < mantissa_range.minimum || mantissa > mantissa_range.maximum) {
            continue;
        }
        const double error = fabs(value - product(mantissa, exponent));
        if (!found || error < best_error) {
            found = true;
            best_error = error;
            best_mantissa = mantissa;
            best_exponent = exponent;
            if (error == 0.0) {
                break;
            }
        }
    }
    if (!found) {
        btsig_error out_of_range = {0};
        out_of_range.status = BTSIG_OUT_OF_RANGE;
        return out_of_range;
    }
    chosen->mantissa = best_mantissa;
    chosen->exponent = best_exponent;
    btsig_error ok = {0};
    return ok;
}

static btsig_error decode(int64_t raw, const DecimalFloat* format, double* out) {
    if (raw == format->positive_infinity) {
        *out = INFINITY;
        btsig_error ok = {0};
        return ok;
    }
    if (raw == format->negative_infinity) {
        *out = -INFINITY;
        btsig_error ok = {0};
        return ok;
    }
    if (raw == format->nan) {
        *out = NAN;
        btsig_error ok = {0};
        return ok;
    }
    if (raw == format->nres || raw == format->reserved) {
        btsig_error out_of_range = {0};
        out_of_range.status = BTSIG_OUT_OF_RANGE;
        return out_of_range;
    }
    const int mantissa = sign_extend((int)(raw & field_mask(format->mantissa_bits)), format->mantissa_bits);
    const int exponent =
        sign_extend((int)((raw >> format->mantissa_bits) & field_mask(format->exponent_bits)), format->exponent_bits);
    const double value = product(mantissa, exponent);
    if (!isfinite(value)) {
        btsig_error out_of_range = {0};
        out_of_range.status = BTSIG_OUT_OF_RANGE;
        return out_of_range;
    }
    *out = value;
    btsig_error ok = {0};
    return ok;
}

static int64_t pack(int mantissa, int exponent, const DecimalFloat* format) {
    const int64_t mantissa_bits = (int64_t)twos_bits(mantissa, format->mantissa_bits);
    const int64_t exponent_bits = (int64_t)twos_bits(exponent, format->exponent_bits);
    return (mantissa_bits & field_mask(format->mantissa_bits)) |
           ((exponent_bits & field_mask(format->exponent_bits)) << format->mantissa_bits);
}

static btsig_error encode(double value, const DecimalFloat* format, int64_t* out) {
    if (isnan(value)) {
        *out = format->nan;
        btsig_error ok = {0};
        return ok;
    }
    if (isinf(value)) {
        *out = signbit(value) ? format->negative_infinity : format->positive_infinity;
        btsig_error ok = {0};
        return ok;
    }
    MantissaExponent chosen = {0};
    const btsig_error chosen_error = choose(value, format->exponent, format->mantissa, &chosen);
    if (chosen_error.status != BTSIG_OK) {
        return chosen_error;
    }
    const int64_t packed = pack(chosen.mantissa, chosen.exponent, format);
    if (is_special(packed, format)) {
        btsig_error out_of_range = {0};
        out_of_range.status = BTSIG_OUT_OF_RANGE;
        return out_of_range;
    }
    *out = packed;
    btsig_error ok = {0};
    return ok;
}

btsig_error btsig_wire_decode_medfloat16(int64_t raw, double* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    return decode(raw, &kSfloat, value);
}

btsig_error btsig_wire_encode_medfloat16(double value, int64_t* raw) {
    if (raw == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    return encode(value, &kSfloat, raw);
}

btsig_error btsig_wire_decode_medfloat32(int64_t raw, double* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    return decode(raw, &kFloat, value);
}

btsig_error btsig_wire_encode_medfloat32(double value, int64_t* raw) {
    if (raw == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        return invalid;
    }
    return encode(value, &kFloat, raw);
}
