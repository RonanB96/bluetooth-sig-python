#ifndef BTSIG_WIRE_DETAIL_MEDFLOAT_HPP
#define BTSIG_WIRE_DETAIL_MEDFLOAT_HPP

#include "btsig/types/expected.hpp"

#include <cstdint>

namespace btsig::wire::detail {

// IEEE 11073-20601 words.
[[nodiscard]] expected<double> decode_medfloat16(std::int64_t raw);
[[nodiscard]] expected<std::int64_t> encode_medfloat16(double value);
[[nodiscard]] expected<double> decode_medfloat32(std::int64_t raw);
[[nodiscard]] expected<std::int64_t> encode_medfloat32(double value);

} // namespace btsig::wire::detail

#endif
