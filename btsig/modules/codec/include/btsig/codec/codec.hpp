#ifndef BTSIG_CODEC_CODEC_HPP
#define BTSIG_CODEC_CODEC_HPP

#include "btsig/codec/codec.h"
#include "btsig/schema/descriptor.hpp"

namespace btsig {

inline btsig_error decode(const CharacteristicDescriptor& descriptor, btsig_bytes input, const btsig_context* context,
                          void* value, std::size_t value_size) {
    return btsig_codec_decode(reinterpret_cast<const btsig_characteristic_descriptor*>(&descriptor), input, context,
                              value, value_size);
}

inline btsig_error encode(const CharacteristicDescriptor& descriptor, const void* value, std::size_t value_size,
                          std::uint8_t* out, std::size_t out_size, std::size_t* written) {
    return btsig_codec_encode(reinterpret_cast<const btsig_characteristic_descriptor*>(&descriptor), value, value_size,
                              out, out_size, written);
}

} // namespace btsig

#endif
