#include "btsig/wire/word.hpp"

#include "ieee754.h"
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
        double value = 0.0;
        const btsig_error error = btsig_wire_decode_binary32(raw, &value);
        if (error.status == BTSIG_OK) {
            return value;
        }
        return unexpected<double>(error);
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
        std::int64_t raw = 0;
        const btsig_error error = btsig_wire_encode_binary32(value, &raw);
        if (error.status == BTSIG_OK) {
            return raw;
        }
        return unexpected<std::int64_t>(error);
    }
    return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
}

} // namespace btsig::wire
