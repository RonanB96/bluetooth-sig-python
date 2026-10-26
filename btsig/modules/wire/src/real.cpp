#include "btsig/wire/word.hpp"

#include "ieee754.hpp"
#include "medfloat.hpp"

namespace btsig::wire {

expected<double> decode_real(wire_type type, std::int64_t raw) {
    if (type == wire_type::medfloat16) {
        return detail::decode_medfloat16(raw);
    }
    if (type == wire_type::medfloat32) {
        return detail::decode_medfloat32(raw);
    }
    if (type == wire_type::float32) {
        return detail::decode_binary32(raw);
    }
    return unexpected_status<double>(BTSIG_INVALID_ARGUMENT);
}

expected<std::int64_t> encode_real(wire_type type, double value) {
    if (type == wire_type::medfloat16) {
        return detail::encode_medfloat16(value);
    }
    if (type == wire_type::medfloat32) {
        return detail::encode_medfloat32(value);
    }
    if (type == wire_type::float32) {
        return detail::encode_binary32(value);
    }
    return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
}

} // namespace btsig::wire
