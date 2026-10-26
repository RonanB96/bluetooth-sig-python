#include "btsig/wire/utf8.hpp"

#include <cstdint>
#include <cstring>
#include <locale>

namespace btsig::wire {
namespace {

// C++17 converts UTF-8 to UTF-32 with this facet. in() returns an error code for a bad
// sequence. mbrtoc32 follows the C locale, which is a different encoding from the wire.
constexpr std::size_t kDecodeWindow = 8;

bool well_formed(span<const std::uint8_t> data) {
    if (data.size() == 0) {
        return true;
    }
    const std::codecvt<char32_t, char, std::mbstate_t>& facet =
        std::use_facet<std::codecvt<char32_t, char, std::mbstate_t>>(std::locale::classic());
    std::mbstate_t state{};
    const char* next = reinterpret_cast<const char*>(data.data());
    const char* const end = next + data.size();
    char32_t decoded[kDecodeWindow];
    while (next != end) {
        const char* const from = next;
        char32_t* produced = nullptr;
        const std::codecvt_base::result result =
            facet.in(state, from, end, next, decoded, decoded + kDecodeWindow, produced);
        if (result != std::codecvt_base::ok && result != std::codecvt_base::partial) {
            return false;
        }
        // No progress means a truncated sequence at the end of the value.
        if (next == from) {
            return false;
        }
    }
    return true;
}

bool null_span(const std::uint8_t* data, std::size_t size) {
    return size != 0 && data == nullptr;
}

btsig_status validated_copy(span<const std::uint8_t> data, span<std::uint8_t> destination) {
    if (null_span(data.data(), data.size()) || null_span(destination.data(), destination.size())) {
        return BTSIG_INVALID_ARGUMENT;
    }
    if (data.size() > destination.size()) {
        return BTSIG_LENGTH_MISMATCH;
    }
    if (!well_formed(data)) {
        return BTSIG_INVALID_ARGUMENT;
    }
    if (data.size() != 0) {
        std::memcpy(destination.data(), data.data(), data.size());
    }
    return BTSIG_OK;
}

} // namespace

expected<std::size_t> read_utf8(span<const std::uint8_t> data, span<std::uint8_t> destination) {
    const btsig_status status = validated_copy(data, destination);
    if (status != BTSIG_OK) {
        return unexpected_status<std::size_t>(status);
    }
    return data.size();
}

btsig_error write_utf8(span<const std::uint8_t> data, span<std::uint8_t> out) {
    btsig_error error{};
    error.status = validated_copy(data, out);
    return error;
}

} // namespace btsig::wire
