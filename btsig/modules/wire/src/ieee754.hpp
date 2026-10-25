#ifndef BTSIG_WIRE_DETAIL_IEEE754_HPP
#define BTSIG_WIRE_DETAIL_IEEE754_HPP

#include <cstdint>

namespace btsig::wire::detail {

// IEEE-754 binary32, widened to double.
[[nodiscard]] bool decode_binary32(std::int64_t raw, double* value);
[[nodiscard]] bool encode_binary32(double value, std::int64_t* raw);

} // namespace btsig::wire::detail

#endif
