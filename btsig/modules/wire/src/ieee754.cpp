#include "ieee754.hpp"

#include <cstdint>
#include <cstring>

namespace btsig::wire::detail {
namespace {

float binary32_from_bits(std::uint32_t bits) {
    float value = 0.0F;
    std::memcpy(&value, &bits, sizeof value);
    return value;
}

std::uint32_t bits_from_binary32(float value) {
    std::uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof bits);
    return bits;
}

} // namespace

expected<double> decode_binary32(std::int64_t raw) {
    return static_cast<double>(binary32_from_bits(static_cast<std::uint32_t>(raw)));
}

expected<std::int64_t> encode_binary32(double value) {
    return bits_from_binary32(static_cast<float>(value));
}

} // namespace btsig::wire::detail
