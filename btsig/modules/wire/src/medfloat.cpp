#include "medfloat.hpp"

#include <cmath>
#include <cstdint>
#include <limits>

namespace btsig::wire::detail {
namespace {

double decade_power(int exponent) {
    double decade = 1.0;
    if (exponent >= 0) {
        for (int step = 0; step < exponent; ++step) {
            decade *= 10.0;
        }
        return decade;
    }
    for (int step = exponent; step < 0; ++step) {
        decade *= 10.0;
    }
    return 1.0 / decade;
}

int sign_extend(int value, int bits) {
    const int sign = 1 << (bits - 1);
    if ((value & sign) != 0) {
        return value - (1 << bits);
    }
    return value;
}

// SFLOAT specials: GSS v9 Table 2.1 and CGM Service v1.0.2 Table 3.8.
constexpr std::int64_t kSfloatPositiveInfinity = 0x07FE;
constexpr std::int64_t kSfloatNan = 0x07FF;
constexpr std::int64_t kSfloatNres = 0x0800;
constexpr std::int64_t kSfloatReserved = 0x0801;
constexpr std::int64_t kSfloatNegativeInfinity = 0x0802;
constexpr int kSfloatExponentMin = -8;
constexpr int kSfloatExponentMax = 7;
constexpr int kSfloatMantissaMin = -2048;
constexpr int kSfloatMantissaMax = 2047;

// FLOAT specials: GSS v9 Table 2.1 and Generic Health Sensor Service Table 1.2.
constexpr std::int64_t kFloatPositiveInfinity = 0x007FFFFE;
constexpr std::int64_t kFloatNan = 0x007FFFFF;
constexpr std::int64_t kFloatNres = 0x00800000;
constexpr std::int64_t kFloatReserved = 0x00800001;
constexpr std::int64_t kFloatNegativeInfinity = 0x00800002;
constexpr int kFloatExponentMin = -128;
constexpr int kFloatExponentMax = 127;
constexpr int kFloatMantissaMin = -8388608;
constexpr int kFloatMantissaMax = 8388607;

bool sfloat_special(std::int64_t raw) {
    return raw == kSfloatNan || raw == kSfloatNres || raw == kSfloatPositiveInfinity ||
           raw == kSfloatNegativeInfinity || raw == kSfloatReserved;
}

bool float_special(std::int64_t raw) {
    return raw == kFloatNan || raw == kFloatNres || raw == kFloatPositiveInfinity || raw == kFloatNegativeInfinity ||
           raw == kFloatReserved;
}

bool choose(double value, int exponent_min, int exponent_max, int mantissa_min, int mantissa_max, int* mantissa_out,
            int* exponent_out) {
    bool found = false;
    int best_mantissa = 0;
    int best_exponent = 0;
    double best_error = std::numeric_limits<double>::infinity();
    for (int exponent = exponent_min; exponent <= exponent_max; ++exponent) {
        const double potential = value * decade_power(-exponent);
        const auto mantissa = static_cast<int>(std::llround(potential));
        if (mantissa < mantissa_min || mantissa > mantissa_max) {
            continue;
        }
        const double actual = static_cast<double>(mantissa) * decade_power(exponent);
        const double error = std::fabs(value - actual);
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
        return false;
    }
    *mantissa_out = best_mantissa;
    *exponent_out = best_exponent;
    return true;
}

} // namespace

bool decode_medfloat16(std::int64_t raw, double* value) {
    if (sfloat_special(raw)) {
        return false;
    }
    // Two's-complement 4-bit exponent, then 12-bit mantissa (IDS v1.0.2, Table 6.1).
    const int mantissa = sign_extend(static_cast<int>(raw & 0x0FFF), 12);
    const int exponent = sign_extend(static_cast<int>((raw >> 12) & 0x0F), 4);
    *value = static_cast<double>(mantissa) * decade_power(exponent);
    return std::isfinite(*value);
}

bool encode_medfloat16(double value, std::int64_t* raw) {
    int mantissa = 0;
    int exponent = 0;
    if (!choose(value, kSfloatExponentMin, kSfloatExponentMax, kSfloatMantissaMin, kSfloatMantissaMax, &mantissa,
                &exponent)) {
        return false;
    }
    if (mantissa < 0) {
        mantissa += 1 << 12;
    }
    if (exponent < 0) {
        exponent += 1 << 4;
    }
    const auto packed =
        (static_cast<std::int64_t>(mantissa) & 0x0FFF) | ((static_cast<std::int64_t>(exponent) & 0x0F) << 12);
    if (sfloat_special(packed)) {
        return false;
    }
    *raw = packed;
    return true;
}

bool decode_medfloat32(std::int64_t raw, double* value) {
    if (float_special(raw)) {
        return false;
    }
    // Signed exponent octet, then signed 24-bit mantissa (GHS, Section 1.5).
    const int mantissa = sign_extend(static_cast<int>(raw & 0x00FFFFFF), 24);
    const int exponent = sign_extend(static_cast<int>((raw >> 24) & 0xFF), 8);
    *value = static_cast<double>(mantissa) * decade_power(exponent);
    return std::isfinite(*value);
}

bool encode_medfloat32(double value, std::int64_t* raw) {
    int mantissa = 0;
    int exponent = 0;
    if (!choose(value, kFloatExponentMin, kFloatExponentMax, kFloatMantissaMin, kFloatMantissaMax, &mantissa,
                &exponent)) {
        return false;
    }
    if (mantissa < 0) {
        mantissa += 1 << 24;
    }
    if (exponent < 0) {
        exponent += 1 << 8;
    }
    const auto packed =
        (static_cast<std::int64_t>(mantissa) & 0x00FFFFFF) | ((static_cast<std::int64_t>(exponent) & 0xFF) << 24);
    if (float_special(packed)) {
        return false;
    }
    *raw = packed;
    return true;
}

} // namespace btsig::wire::detail
