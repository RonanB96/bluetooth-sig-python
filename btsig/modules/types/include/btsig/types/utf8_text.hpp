#ifndef BTSIG_TYPES_UTF8_TEXT_HPP
#define BTSIG_TYPES_UTF8_TEXT_HPP

#include "btsig/types/utf8_text.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace btsig {

// Bluetooth Core Specification v5.4, Vol 3, Part F, 3.2.9.
inline constexpr std::size_t kMaxAttributeValueOctets = 512;

// Counted UTF-8 text. `size` is the number of initial octets in `data` that hold the text.
// The array bound is the maximum. The wire image is those octets, with no terminator.
template <std::size_t Capacity> struct utf8_text {
    static_assert(Capacity > 0);
    static_assert(Capacity <= kMaxAttributeValueOctets);

    std::uint16_t size;
    std::array<std::uint8_t, Capacity> data;
};

// Bytes occupied by `utf8_text<capacity>`, including tail padding to `uint16_t` alignment.
constexpr std::size_t stored_utf8_bytes(std::uint16_t capacity) {
    return btsig_stored_utf8_bytes(capacity);
}

static_assert(stored_utf8_bytes(1) == sizeof(utf8_text<1>));
static_assert(stored_utf8_bytes(16) == sizeof(utf8_text<16>));
static_assert(stored_utf8_bytes(120) == sizeof(utf8_text<120>));
static_assert(stored_utf8_bytes(512) == sizeof(utf8_text<512>));
static_assert(std::is_standard_layout_v<utf8_text<16>>);
static_assert(std::is_trivially_copyable_v<utf8_text<16>>);

} // namespace btsig

#endif
