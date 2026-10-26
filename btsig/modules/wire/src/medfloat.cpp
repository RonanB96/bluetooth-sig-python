#include "medfloat.hpp"

#include <cmath>
#include <cstdint>
#include <limits>

namespace btsig::wire::detail {
namespace {

struct IntRange {
    int minimum;
    int maximum;
};

// Exponent then mantissa, base 10. Specials are exact words, not products.
struct DecimalFloat {
    int exponent_bits;
    int mantissa_bits;
    IntRange exponent;
    IntRange mantissa;
    std::int64_t positive_infinity;
    std::int64_t negative_infinity;
    std::int64_t nan;
    std::int64_t nres;
    std::int64_t reserved;
};

int field_mask(int bits) {
    return (1 << bits) - 1;
}

bool is_special(std::int64_t raw, const DecimalFloat& format) {
    return raw == format.positive_infinity || raw == format.negative_infinity || raw == format.nan ||
           raw == format.nres || raw == format.reserved;
}

// ISO/IEEE 11073-20601 SFLOAT-Type, Personal Health Devices Transcoding White Paper V15r00 §2.2.2.
constexpr DecimalFloat sfloat_format() {
    DecimalFloat format{};
    format.exponent_bits = 4;
    format.mantissa_bits = 12;
    format.exponent = {-8, 7};
    format.mantissa = {-2048, 2047};
    format.positive_infinity = 0x07FE;
    format.negative_infinity = 0x0802;
    format.nan = 0x07FF;
    format.nres = 0x0800;
    format.reserved = 0x0801;
    return format;
}

// ISO/IEEE 11073-20601 FLOAT-Type, Personal Health Devices Transcoding White Paper V15r00 §2.2.1.
constexpr DecimalFloat float_format() {
    DecimalFloat format{};
    format.exponent_bits = 8;
    format.mantissa_bits = 24;
    format.exponent = {-128, 127};
    format.mantissa = {-8388608, 8388607};
    format.positive_infinity = 0x007FFFFE;
    format.negative_infinity = 0x00800002;
    format.nan = 0x007FFFFF;
    format.nres = 0x00800000;
    format.reserved = 0x00800001;
    return format;
}

constexpr DecimalFloat kSfloat = sfloat_format();
constexpr DecimalFloat kFloat = float_format();

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

int twos_bits(int value, int bits) {
    if (value < 0) {
        return value + (1 << bits);
    }
    return value;
}

double product(int mantissa, int exponent) {
    return static_cast<double>(mantissa) * decade_power(exponent);
}

struct MantissaExponent {
    int mantissa;
    int exponent;
};

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
        const double error = std::fabs(value - product(mantissa, exponent));
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

expected<double> decode(std::int64_t raw, const DecimalFloat& format) {
    if (raw == format.positive_infinity) {
        return std::numeric_limits<double>::infinity();
    }
    if (raw == format.negative_infinity) {
        return -std::numeric_limits<double>::infinity();
    }
    if (raw == format.nan) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    if (raw == format.nres || raw == format.reserved) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    const int mantissa = sign_extend(static_cast<int>(raw & field_mask(format.mantissa_bits)), format.mantissa_bits);
    const int exponent = sign_extend(static_cast<int>((raw >> format.mantissa_bits) & field_mask(format.exponent_bits)),
                                     format.exponent_bits);
    const double value = product(mantissa, exponent);
    if (!std::isfinite(value)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    return value;
}

std::int64_t pack(int mantissa, int exponent, const DecimalFloat& format) {
    const auto mantissa_bits = static_cast<std::int64_t>(twos_bits(mantissa, format.mantissa_bits));
    const auto exponent_bits = static_cast<std::int64_t>(twos_bits(exponent, format.exponent_bits));
    return (mantissa_bits & field_mask(format.mantissa_bits)) |
           ((exponent_bits & field_mask(format.exponent_bits)) << format.mantissa_bits);
}

expected<std::int64_t> encode(double value, const DecimalFloat& format) {
    if (std::isnan(value)) {
        return format.nan;
    }
    if (std::isinf(value)) {
        return std::signbit(value) ? format.negative_infinity : format.positive_infinity;
    }
    const auto chosen = choose(value, format.exponent, format.mantissa);
    if (!chosen) {
        return unexpected_status<std::int64_t>(chosen.error().status);
    }
    const std::int64_t packed = pack(chosen.value().mantissa, chosen.value().exponent, format);
    if (is_special(packed, format)) {
        return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
    }
    return packed;
}

} // namespace

expected<double> decode_medfloat16(std::int64_t raw) {
    return decode(raw, kSfloat);
}

expected<std::int64_t> encode_medfloat16(double value) {
    return encode(value, kSfloat);
}

expected<double> decode_medfloat32(std::int64_t raw) {
    return decode(raw, kFloat);
}

expected<std::int64_t> encode_medfloat32(double value) {
    return encode(value, kFloat);
}

} // namespace btsig::wire::detail
