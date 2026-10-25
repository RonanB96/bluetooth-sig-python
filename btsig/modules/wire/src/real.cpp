#include "btsig/wire/word.hpp"

#include "ieee754.hpp"
#include "medfloat.hpp"

namespace btsig::wire {

bool decode_real(wire_type type, std::int64_t raw, double* value) {
    if (type == wire_type::medfloat16) {
        return detail::decode_medfloat16(raw, value);
    }
    if (type == wire_type::medfloat32) {
        return detail::decode_medfloat32(raw, value);
    }
    if (type == wire_type::float32) {
        return detail::decode_binary32(raw, value);
    }
    return false;
}

bool encode_real(wire_type type, double value, std::int64_t* raw) {
    if (type == wire_type::medfloat16) {
        return detail::encode_medfloat16(value, raw);
    }
    if (type == wire_type::medfloat32) {
        return detail::encode_medfloat32(value, raw);
    }
    if (type == wire_type::float32) {
        return detail::encode_binary32(value, raw);
    }
    return false;
}

} // namespace btsig::wire
