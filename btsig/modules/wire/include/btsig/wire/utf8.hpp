#ifndef BTSIG_WIRE_UTF8_HPP
#define BTSIG_WIRE_UTF8_HPP

#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig::wire {

// BTSIG_INVALID_ARGUMENT when `data` is not well-formed UTF-8, or a pointer is null with a non-zero size.
[[nodiscard]] btsig_status check_utf8(span<const std::uint8_t> data);

// Copy a well-formed UTF-8 value into `destination`.
// BTSIG_INVALID_ARGUMENT when `data` is not well-formed UTF-8, or a pointer is null with a non-zero size.
// BTSIG_LENGTH_MISMATCH when `data.size()` is greater than `destination.size()`.
// The returned size is the octet count copied.
[[nodiscard]] expected<std::size_t> read_utf8(span<const std::uint8_t> data, span<std::uint8_t> destination);

// Copy `data` to `out` when `data` is well-formed UTF-8 and fits.
// BTSIG_INVALID_ARGUMENT when `data` is not well-formed UTF-8, or a pointer is null with a non-zero size.
// BTSIG_LENGTH_MISMATCH when `data` is longer than `out`.
[[nodiscard]] btsig_error write_utf8(span<const std::uint8_t> data, span<std::uint8_t> out);

} // namespace btsig::wire

#endif
