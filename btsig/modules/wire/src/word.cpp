#include "btsig/wire/word.hpp"

#include <cstddef>
#include <cstdint>
#include <limits>

namespace btsig::wire {
namespace {

bool is_signed(wire_type type) {
    switch (type) {
    case wire_type::sint8:
    case wire_type::sint16:
    case wire_type::sint24:
    case wire_type::sint32:
        return true;
    case wire_type::uint8:
    case wire_type::uint16:
    case wire_type::uint24:
    case wire_type::uint32:
    case wire_type::uint48:
    case wire_type::uint64:
    case wire_type::boolean8:
    case wire_type::boolean16:
    case wire_type::boolean24:
    case wire_type::boolean32:
    case wire_type::medfloat16:
    case wire_type::medfloat32:
    case wire_type::float32:
    case wire_type::utf8:
    case wire_type::uint1:
    case wire_type::uint2:
        return false;
    }
    return false;
}

} // namespace

std::size_t width(wire_type type) {
    switch (type) {
    case wire_type::uint8:
    case wire_type::sint8:
    case wire_type::boolean8:
        return 1;
    case wire_type::uint16:
    case wire_type::sint16:
    case wire_type::boolean16:
    case wire_type::medfloat16:
        return 2;
    case wire_type::uint24:
    case wire_type::sint24:
    case wire_type::boolean24:
        return 3;
    case wire_type::uint32:
    case wire_type::sint32:
    case wire_type::boolean32:
    case wire_type::medfloat32:
    case wire_type::float32:
        return 4;
    case wire_type::uint48:
        return 6;
    case wire_type::uint64:
        return 8;
    case wire_type::utf8:
    case wire_type::uint1:
    case wire_type::uint2:
        return 0;
    }
    return 0;
}

bool is_real(wire_type type) {
    return type == wire_type::medfloat16 || type == wire_type::medfloat32 || type == wire_type::float32;
}

expected<std::int64_t> read(span<const std::uint8_t> data, wire_type type) {
    const std::size_t octets = width(type);
    // width returns 0 for an unknown enumerator. bits_in_wire is uint32_t,
    // so a zero width wraps bits_in_wire - 1 before the sign-bit shift. A width
    // above 8 shifts a byte out of uint64_t.
    if (octets == 0 || octets > sizeof(std::uint64_t) || data.data() == nullptr || data.size() < octets) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    std::uint64_t bits = 0;
    for (std::size_t index = 0; index < octets; ++index) {
        const auto shift = static_cast<std::uint32_t>(index) * 8U;
        bits |= static_cast<std::uint64_t>(data.data()[index]) << shift;
    }
    if (!is_signed(type)) {
        if (bits > static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
            return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
        }
        return static_cast<std::int64_t>(bits);
    }
    // Two's complement, sign bit most significant (Core Specification 6.3, Volume 1, Part E, Section 2.9.1).
    const auto bits_in_wire = static_cast<std::uint32_t>(octets * 8U);
    if (bits_in_wire < 64U && (bits & (std::uint64_t{1} << (bits_in_wire - 1U))) != 0U) {
        bits |= ~((std::uint64_t{1} << bits_in_wire) - 1U);
    }
    return static_cast<std::int64_t>(bits);
}

btsig_error write(span<std::uint8_t> out, std::int64_t raw) {
    btsig_error error{};
    // A shift of 64 bits or more is undefined for uint64_t.
    if (out.data() == nullptr || out.size() == 0 || out.size() > sizeof(std::uint64_t)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    const auto bits = static_cast<std::uint64_t>(raw);
    for (std::size_t index = 0; index < out.size(); ++index) {
        const auto shift = static_cast<std::uint32_t>(index) * 8U;
        out.data()[index] = static_cast<std::uint8_t>(bits >> shift);
    }
    return error;
}

} // namespace btsig::wire
