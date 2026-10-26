#ifndef BTSIG_WIRE_DETAIL_IEEE754_HPP
#define BTSIG_WIRE_DETAIL_IEEE754_HPP

#include "btsig/types/expected.hpp"

#include <cstdint>

namespace btsig::wire::detail {

// IEEE 754 binary32 widened to double (Core Specification 6.3, Volume 1, Part E, Section 2.9.1).
[[nodiscard]] expected<double> decode_binary32(std::int64_t raw);
[[nodiscard]] expected<std::int64_t> encode_binary32(double value);

} // namespace btsig::wire::detail

#endif
