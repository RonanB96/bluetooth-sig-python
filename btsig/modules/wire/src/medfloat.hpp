#ifndef BTSIG_WIRE_DETAIL_MEDFLOAT_HPP
#define BTSIG_WIRE_DETAIL_MEDFLOAT_HPP

#include <cstdint>

namespace btsig::wire::detail {

// IEEE 11073-20601 words.
[[nodiscard]] bool decode_medfloat16(std::int64_t raw, double* value);
[[nodiscard]] bool encode_medfloat16(double value, std::int64_t* raw);
[[nodiscard]] bool decode_medfloat32(std::int64_t raw, double* value);
[[nodiscard]] bool encode_medfloat32(double value, std::int64_t* raw);

} // namespace btsig::wire::detail

#endif
