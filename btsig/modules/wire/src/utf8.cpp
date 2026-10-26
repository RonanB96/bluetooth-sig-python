#include "btsig/wire/utf8.hpp"

#include <cstdint>
#include <cstring>

namespace btsig::wire {
namespace {

constexpr std::uint8_t kAsciiMax = 0x7F;
constexpr std::uint8_t kTwoByteLeadMin = 0xC2;
constexpr std::uint8_t kThreeByteLeadMin = 0xE0;
constexpr std::uint8_t kFourByteLeadMin = 0xF0;
constexpr std::uint8_t kFourByteLeadMax = 0xF4;
constexpr std::uint8_t kContinuationPrefix = 0x80;
constexpr std::uint8_t kContinuationMask = 0xC0;
constexpr std::uint32_t kMaxCodePoint = 0x10FFFF;
constexpr std::uint32_t kSurrogateMin = 0xD800;
constexpr std::uint32_t kSurrogateMax = 0xDFFF;

bool continuation(std::uint8_t byte) {
    return (byte & kContinuationMask) == kContinuationPrefix;
}

// Unicode well-formed UTF-8: no overlong sequences, no surrogates, no code point above U+10FFFF.
// The octets are copied through, so this only accepts or rejects the sequence.
bool well_formed(span<const std::uint8_t> data) {
    std::size_t index = 0;
    while (index < data.size()) {
        const std::uint8_t lead = data.data()[index];
        if (lead <= kAsciiMax) {
            index += 1;
            continue;
        }
        std::size_t need = 0;
        std::uint32_t minimum = 0;
        std::uint32_t code = 0;
        if (lead >= kTwoByteLeadMin && lead < kThreeByteLeadMin) {
            need = 2;
            minimum = 0x80;
            code = lead & 0x1FU;
        } else if (lead >= kThreeByteLeadMin && lead < kFourByteLeadMin) {
            need = 3;
            minimum = 0x800;
            code = lead & 0x0FU;
        } else if (lead >= kFourByteLeadMin && lead <= kFourByteLeadMax) {
            need = 4;
            minimum = 0x10000;
            code = lead & 0x07U;
        } else {
            return false;
        }
        if (index + need > data.size()) {
            return false;
        }
        for (std::size_t extra = 1; extra < need; ++extra) {
            const std::uint8_t byte = data.data()[index + extra];
            if (!continuation(byte)) {
                return false;
            }
            code = (code << 6U) | (byte & 0x3FU);
        }
        if (code < minimum || code > kMaxCodePoint || (code >= kSurrogateMin && code <= kSurrogateMax)) {
            return false;
        }
        index += need;
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
