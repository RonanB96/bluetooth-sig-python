#include "ieee754.hpp"

#include <cmath>
#include <cstdint>
#include <cstring>

namespace btsig::wire::detail {

bool decode_binary32(std::int64_t raw, double* value) {
    const auto bits = static_cast<std::uint32_t>(raw);
    float binary32 = 0.0F;
    std::memcpy(&binary32, &bits, sizeof binary32);
    if (!std::isfinite(binary32)) {
        return false;
    }
    *value = static_cast<double>(binary32);
    return true;
}

bool encode_binary32(double value, std::int64_t* raw) {
    const auto binary32 = static_cast<float>(value);
    if (!std::isfinite(binary32)) {
        return false;
    }
    std::uint32_t bits = 0;
    std::memcpy(&bits, &binary32, sizeof bits);
    *raw = bits;
    return true;
}

} // namespace btsig::wire::detail
