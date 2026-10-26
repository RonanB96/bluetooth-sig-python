// Handwritten override. This codec replaces a generated codec for the same characteristic id.
// Core Specification 6.3, Volume 3, Part C, section 12.1: UTF-8, 0 to 248 octets.
#ifndef BTSIG_DEVICE_NAME_H
#define BTSIG_DEVICE_NAME_H

#include "btsig/types/status.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum { btsig_device_name_octets = 248 };

typedef struct btsig_device_name {
    uint16_t device_name_length;
    uint8_t device_name[btsig_device_name_octets];
} btsig_device_name;

btsig_error btsig_decode_device_name(btsig_bytes input, const btsig_context* context, btsig_device_name* value);

btsig_error btsig_encode_device_name(const btsig_device_name* value, uint8_t* out, size_t out_size, size_t* written);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_DEVICE_NAME_H
