#include "btsig/wire/subbyte.hpp"

namespace btsig::wire {
namespace {

bool covers(std::size_t size, std::size_t bit_offset, std::size_t width) {
    if (width < kMinSubbyteBits || width > kMaxSubbyteBits) {
        return false;
    }
    const std::size_t last = bit_offset + width - 1U;
    return size > last / kBitsPerOctet;
}

} // namespace

std::size_t bit_width(wire_type type) {
    if (type == wire_type::uint1) {
        return kUint1Bits;
    }
    if (type == wire_type::uint2) {
        return kUint2Bits;
    }
    return 0;
}

expected<std::int64_t> read_bits(span<const std::uint8_t> data, std::size_t bit_offset, std::size_t width) {
    if (data.data() == nullptr || !covers(data.size(), bit_offset, width)) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    std::uint64_t value = 0;
    for (std::size_t bit = 0; bit < width; ++bit) {
        const std::size_t index = bit_offset + bit;
        const std::uint8_t byte = data.data()[index / kBitsPerOctet];
        if ((byte & static_cast<std::uint8_t>(1U << (index % kBitsPerOctet))) != 0) {
            value |= std::uint64_t{1} << bit;
        }
    }
    return static_cast<std::int64_t>(value);
}

btsig_error write_bits(span<std::uint8_t> out, std::size_t bit_offset, std::size_t width, std::int64_t raw) {
    btsig_error error{};
    if (out.data() == nullptr || !covers(out.size(), bit_offset, width)) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    const auto limit = std::int64_t{1} << width;
    if (raw < 0 || raw >= limit) {
        error.status = BTSIG_OUT_OF_RANGE;
        return error;
    }
    for (std::size_t bit = 0; bit < width; ++bit) {
        if ((raw & (std::int64_t{1} << bit)) == 0) {
            continue;
        }
        const std::size_t index = bit_offset + bit;
        out.data()[index / kBitsPerOctet] = static_cast<std::uint8_t>(
            out.data()[index / kBitsPerOctet] | static_cast<std::uint8_t>(1U << (index % kBitsPerOctet)));
    }
    return error;
}

} // namespace btsig::wire
