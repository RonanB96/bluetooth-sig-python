#ifndef BTSIG_WIRE_SUBBYTE_HPP
#define BTSIG_WIRE_SUBBYTE_HPP

#include "btsig/schema/descriptor.hpp"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig::wire {

inline constexpr std::size_t kBitsPerOctet = 8;
inline constexpr std::size_t kUint1Bits = 1;
inline constexpr std::size_t kUint2Bits = 2;
inline constexpr std::size_t kMinSubbyteBits = kUint1Bits;
inline constexpr std::size_t kMaxSubbyteBits = kBitsPerOctet - 1;

// Bit width of uint1 or uint2. Zero for every other wire type.
[[nodiscard]] std::size_t bit_width(wire_type type);

// Read `width` bits starting at `bit_offset`. Bit 0 is the least significant bit of the first octet.
// BTSIG_INVALID_ARGUMENT when the span does not cover the bits, a pointer is null, or `width` is outside
// `kMinSubbyteBits`..`kMaxSubbyteBits`.
[[nodiscard]] expected<std::int64_t> read_bits(span<const std::uint8_t> data, std::size_t bit_offset,
                                               std::size_t width);

// Write the low `width` bits of `raw` at `bit_offset`.
// BTSIG_INVALID_ARGUMENT when the span does not cover the bits or `width` is outside
// `kMinSubbyteBits`..`kMaxSubbyteBits`.
// BTSIG_OUT_OF_RANGE when `raw` is negative or does not fit in `width` bits.
[[nodiscard]] btsig_error write_bits(span<std::uint8_t> out, std::size_t bit_offset, std::size_t width,
                                     std::int64_t raw);

} // namespace btsig::wire

#endif
