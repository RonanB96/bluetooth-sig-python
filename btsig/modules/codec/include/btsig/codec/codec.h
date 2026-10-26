#ifndef BTSIG_CODEC_CODEC_H
#define BTSIG_CODEC_CODEC_H

#include "btsig/schema/descriptor.h"
#include "btsig/types/status.h"

#ifdef __cplusplus
extern "C" {
#endif

btsig_error btsig_codec_decode(const btsig_characteristic_descriptor* descriptor, btsig_bytes input,
                               const btsig_context* context, void* value, size_t value_size);

btsig_error btsig_codec_encode(const btsig_characteristic_descriptor* descriptor, const void* value, size_t value_size,
                               uint8_t* out, size_t out_size, size_t* written);

#ifdef __cplusplus
}
#endif

#endif
