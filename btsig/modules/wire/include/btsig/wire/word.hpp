#ifndef BTSIG_WIRE_WORD_HPP
#define BTSIG_WIRE_WORD_HPP

#include "btsig/schema/descriptor.hpp"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig::wire {

// Octet width of one wire value. Zero means the enumerator is not a known width.
[[nodiscard]] std::size_t width(wire_type type);

// Little-endian word in `data`. BTSIG_INVALID_ARGUMENT when the span is shorter than
// width(type) or the width is unknown. BTSIG_OUT_OF_RANGE when the unsigned word does not fit in int64_t.
[[nodiscard]] expected<std::int64_t> read(span<const std::uint8_t> data, wire_type type);

// Little-endian write of one word. `out.size()` is the octet width.
// BTSIG_INVALID_ARGUMENT when the span is empty, null, or wider than 8 octets.
[[nodiscard]] btsig_error write(span<std::uint8_t> out, std::int64_t raw);

// True for medfloat16, medfloat32, and IEEE-754 binary32.
[[nodiscard]] bool is_real(wire_type type);

// BTSIG_OUT_OF_RANGE for a special pattern or a non-finite result.
// BTSIG_INVALID_ARGUMENT when the wire type is not real, or the value to encode is non-finite.
[[nodiscard]] expected<double> decode_real(wire_type type, std::int64_t raw);
[[nodiscard]] expected<std::int64_t> encode_real(wire_type type, double value);

} // namespace btsig::wire

#endif
