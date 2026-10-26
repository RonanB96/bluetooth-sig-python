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

constexpr int kSfloatMantissaBits = 12;
constexpr int kSfloatExponentBits = 4;
constexpr int kSfloatMantissaMask = (1 << kSfloatMantissaBits) - 1;
constexpr int kSfloatExponentMask = (1 << kSfloatExponentBits) - 1;
constexpr int kFloatMantissaBits = 24;
constexpr int kFloatExponentBits = 8;
constexpr int kFloatMantissaMask = (1 << kFloatMantissaBits) - 1;
constexpr int kFloatExponentMask = (1 << kFloatExponentBits) - 1;

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

struct IntRange {
    int minimum;
    int maximum;
};

struct MantissaExponent {
    int mantissa;
    int exponent;
};

bool sfloat_special(std::int64_t raw) {
    return raw == kSfloatNan || raw == kSfloatNres || raw == kSfloatPositiveInfinity ||
           raw == kSfloatNegativeInfinity || raw == kSfloatReserved;
}

bool float_special(std::int64_t raw) {
    return raw == kFloatNan || raw == kFloatNres || raw == kFloatPositiveInfinity || raw == kFloatNegativeInfinity ||
           raw == kFloatReserved;
}

expected<MantissaExponent> choose(double value, IntRange exponent_range, IntRange mantissa_range) {
    bool found = false;
    int best_mantissa = 0;
    int best_exponent = 0;
    double best_error = std::numeric_limits<double>::infinity();
    for (int exponent = exponent_range.minimum; exponent <= exponent_range.maximum; ++exponent) {
        const double potential = value * decade_power(-exponent);
        const auto mantissa = static_cast<int>(std::llround(potential));
        if (mantissa < mantissa_range.minimum || mantissa > mantissa_range.maximum) {
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
        return unexpected_status<MantissaExponent>(BTSIG_OUT_OF_RANGE);
    }
    return MantissaExponent{best_mantissa, best_exponent};
}

} // namespace

expected<double> decode_medfloat16(std::int64_t raw) {
    if (sfloat_special(raw)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    // Two's-complement 4-bit exponent, then 12-bit mantissa (IDS v1.0.2, Table 6.1).
    const int mantissa = sign_extend(static_cast<int>(raw & kSfloatMantissaMask), kSfloatMantissaBits);
    const int exponent =
        sign_extend(static_cast<int>((raw >> kSfloatMantissaBits) & kSfloatExponentMask), kSfloatExponentBits);
    const double value = static_cast<double>(mantissa) * decade_power(exponent);
    if (!std::isfinite(value)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    return value;
}

expected<std::int64_t> encode_medfloat16(double value) {
    if (!std::isfinite(value)) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    const auto chosen = choose(value, IntRange{kSfloatExponentMin, kSfloatExponentMax},
                               IntRange{kSfloatMantissaMin, kSfloatMantissaMax});
    if (!chosen) {
        return unexpected_status<std::int64_t>(chosen.error().status);
    }
    int mantissa = chosen.value().mantissa;
    int exponent = chosen.value().exponent;
    if (mantissa < 0) {
        mantissa += 1 << kSfloatMantissaBits;
    }
    if (exponent < 0) {
        exponent += 1 << kSfloatExponentBits;
    }
    const auto packed = (static_cast<std::int64_t>(mantissa) & kSfloatMantissaMask) |
                        ((static_cast<std::int64_t>(exponent) & kSfloatExponentMask) << kSfloatMantissaBits);
    if (sfloat_special(packed)) {
        return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
    }
    return packed;
}

expected<double> decode_medfloat32(std::int64_t raw) {
    if (float_special(raw)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    // Signed exponent octet, then signed 24-bit mantissa (GHS, Section 1.5).
    const int mantissa = sign_extend(static_cast<int>(raw & kFloatMantissaMask), kFloatMantissaBits);
    const int exponent =
        sign_extend(static_cast<int>((raw >> kFloatMantissaBits) & kFloatExponentMask), kFloatExponentBits);
    const double value = static_cast<double>(mantissa) * decade_power(exponent);
    if (!std::isfinite(value)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    return value;
}

expected<std::int64_t> encode_medfloat32(double value) {
    if (!std::isfinite(value)) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    const auto chosen =
        choose(value, IntRange{kFloatExponentMin, kFloatExponentMax}, IntRange{kFloatMantissaMin, kFloatMantissaMax});
    if (!chosen) {
        return unexpected_status<std::int64_t>(chosen.error().status);
    }
    int mantissa = chosen.value().mantissa;
    int exponent = chosen.value().exponent;
    if (mantissa < 0) {
        mantissa += 1 << kFloatMantissaBits;
    }
    if (exponent < 0) {
        exponent += 1 << kFloatExponentBits;
    }
    const auto packed = (static_cast<std::int64_t>(mantissa) & kFloatMantissaMask) |
                        ((static_cast<std::int64_t>(exponent) & kFloatExponentMask) << kFloatMantissaBits);
    if (float_special(packed)) {
        return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
    }
    return packed;
}

} // namespace btsig::wire::detail
