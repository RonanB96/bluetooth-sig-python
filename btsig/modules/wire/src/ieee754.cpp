#include "ieee754.hpp"

#include <cmath>
#include <cstdint>
#include <cstring>

namespace btsig::wire::detail {

expected<double> decode_binary32(std::int64_t raw) {
    const auto bits = static_cast<std::uint32_t>(raw);
    float binary32 = 0.0F;
    std::memcpy(&binary32, &bits, sizeof binary32);
    if (!std::isfinite(binary32)) {
        return unexpected_status<double>(BTSIG_OUT_OF_RANGE);
    }
    return static_cast<double>(binary32);
}

expected<std::int64_t> encode_binary32(double value) {
    if (!std::isfinite(value)) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    const auto binary32 = static_cast<float>(value);
    if (!std::isfinite(binary32)) {
        return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
    }
    std::uint32_t bits = 0;
    std::memcpy(&bits, &binary32, sizeof bits);
    return bits;
}

} // namespace btsig::wire::detail
