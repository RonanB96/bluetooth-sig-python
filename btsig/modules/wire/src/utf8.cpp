#include "btsig/wire/utf8.hpp"

#include <cstdint>
#include <cstring>

namespace btsig::wire {
namespace {

// Well-formed UTF-8 lead and continuation bounds.
constexpr std::uint8_t kAsciiMax = 0x7F;
constexpr std::uint8_t kContinuationMask = 0xC0;
constexpr std::uint8_t kContinuationPrefix = 0x80;
constexpr std::uint8_t kContinuationMax = 0xBF;
constexpr std::uint8_t kTwoByteLeadMin = 0xC2;
constexpr std::uint8_t kTwoByteLeadMax = 0xDF;
constexpr std::uint8_t kThreeByteLeadE0 = 0xE0;
constexpr std::uint8_t kE0ContinuationMin = 0xA0;
constexpr std::uint8_t kThreeByteLeadMin = 0xE1;
constexpr std::uint8_t kThreeByteLeadEc = 0xEC;
constexpr std::uint8_t kSurrogateLead = 0xED;
constexpr std::uint8_t kSurrogateContinuationMax = 0x9F;
constexpr std::uint8_t kThreeByteLeadEe = 0xEE;
constexpr std::uint8_t kThreeByteLeadEf = 0xEF;
constexpr std::uint8_t kFourByteLeadF0 = 0xF0;
constexpr std::uint8_t kF0ContinuationMin = 0x90;
constexpr std::uint8_t kFourByteLeadMin = 0xF1;
constexpr std::uint8_t kFourByteLeadMax = 0xF3;
constexpr std::uint8_t kFourByteLeadF4 = 0xF4;
constexpr std::uint8_t kF4ContinuationMax = 0x8F;
constexpr std::size_t kOneOctet = 1;
constexpr std::size_t kTwoOctets = 2;
constexpr std::size_t kThreeOctets = 3;
constexpr std::size_t kFourOctets = 4;

bool continuation(std::uint8_t byte) {
    return (byte & kContinuationMask) == kContinuationPrefix;
}

// Unicode well-formed UTF-8: no overlong sequences and no UTF-16 surrogates.
bool well_formed(span<const std::uint8_t> data) {
    std::size_t index = 0;
    while (index < data.size()) {
        const std::uint8_t lead = data.data()[index];
        if (lead <= kAsciiMax) {
            index += kOneOctet;
            continue;
        }
        if (lead >= kTwoByteLeadMin && lead <= kTwoByteLeadMax) {
            if (index + 1 >= data.size() || !continuation(data.data()[index + 1])) {
                return false;
            }
            index += kTwoOctets;
            continue;
        }
        if (lead == kThreeByteLeadE0) {
            if (index + 2 >= data.size() || data.data()[index + 1] < kE0ContinuationMin ||
                data.data()[index + 1] > kContinuationMax || !continuation(data.data()[index + 2])) {
                return false;
            }
            index += kThreeOctets;
            continue;
        }
        if ((lead >= kThreeByteLeadMin && lead <= kThreeByteLeadEc) || lead == kThreeByteLeadEe ||
            lead == kThreeByteLeadEf) {
            if (index + 2 >= data.size() || !continuation(data.data()[index + 1]) ||
                !continuation(data.data()[index + 2])) {
                return false;
            }
            index += kThreeOctets;
            continue;
        }
        if (lead == kSurrogateLead) {
            if (index + 2 >= data.size() || data.data()[index + 1] < kContinuationPrefix ||
                data.data()[index + 1] > kSurrogateContinuationMax || !continuation(data.data()[index + 2])) {
                return false;
            }
            index += kThreeOctets;
            continue;
        }
        if (lead == kFourByteLeadF0) {
            if (index + 3 >= data.size() || data.data()[index + 1] < kF0ContinuationMin ||
                data.data()[index + 1] > kContinuationMax || !continuation(data.data()[index + 2]) ||
                !continuation(data.data()[index + 3])) {
                return false;
            }
            index += kFourOctets;
            continue;
        }
        if (lead >= kFourByteLeadMin && lead <= kFourByteLeadMax) {
            if (index + 3 >= data.size() || !continuation(data.data()[index + 1]) ||
                !continuation(data.data()[index + 2]) || !continuation(data.data()[index + 3])) {
                return false;
            }
            index += kFourOctets;
            continue;
        }
        if (lead == kFourByteLeadF4) {
            if (index + 3 >= data.size() || data.data()[index + 1] < kContinuationPrefix ||
                data.data()[index + 1] > kF4ContinuationMax || !continuation(data.data()[index + 2]) ||
                !continuation(data.data()[index + 3])) {
                return false;
            }
            index += kFourOctets;
            continue;
        }
        return false;
    }
    return true;
}

bool null_span(const std::uint8_t* data, std::size_t size) {
    return size != 0 && data == nullptr;
}

} // namespace

expected<std::size_t> read_utf8(span<const std::uint8_t> data, span<std::uint8_t> destination) {
    if (null_span(data.data(), data.size()) || null_span(destination.data(), destination.size())) {
        return unexpected_status<std::size_t>(BTSIG_INVALID_ARGUMENT);
    }
    if (data.size() > destination.size()) {
        return unexpected_status<std::size_t>(BTSIG_LENGTH_MISMATCH);
    }
    if (!well_formed(data)) {
        return unexpected_status<std::size_t>(BTSIG_INVALID_ARGUMENT);
    }
    if (data.size() != 0) {
        std::memcpy(destination.data(), data.data(), data.size());
    }
    return data.size();
}

btsig_error write_utf8(span<const std::uint8_t> data, span<std::uint8_t> out) {
    btsig_error error{};
    if (null_span(data.data(), data.size()) || null_span(out.data(), out.size())) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    if (data.size() > out.size()) {
        error.status = BTSIG_LENGTH_MISMATCH;
        return error;
    }
    if (!well_formed(data)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    if (data.size() != 0) {
        std::memcpy(out.data(), data.data(), data.size());
    }
    return error;
}

} // namespace btsig::wire
