#pragma once

#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig::wire {

// Octet width of one wire value. Zero means the enumerator is not a known width.
[[nodiscard]] std::size_t width(wire_type type);

// Little-endian read of one wire word into a signed 64-bit raw value.
// A word that does not fit in int64_t fails.
[[nodiscard]] bool read(const std::uint8_t* data, wire_type type, std::int64_t* raw);

// Little-endian write of a raw word. `octets` is `width(type)`.
void write(std::uint8_t* out, std::size_t octets, std::int64_t raw);

// True for medfloat16, medfloat32, and IEEE-754 binary32.
[[nodiscard]] bool is_real(wire_type type);

// Decode or encode one real wire word. False for a special pattern, a non-finite
// value, or a wire type that is not real.
[[nodiscard]] bool decode_real(wire_type type, std::int64_t raw, double* value);
[[nodiscard]] bool encode_real(wire_type type, double value, std::int64_t* raw);

} // namespace btsig::wire
