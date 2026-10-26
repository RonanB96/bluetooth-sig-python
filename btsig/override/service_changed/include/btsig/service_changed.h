// Handwritten override. This codec replaces a generated codec for the same characteristic id.
// Core Specification 6.3, Volume 3, Part G, section 7.1: two uint16 attribute handles.
#ifndef BTSIG_SERVICE_CHANGED_H
#define BTSIG_SERVICE_CHANGED_H

#include "btsig/types/status.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct btsig_service_changed {
    uint16_t start_handle;
    uint16_t end_handle;
} btsig_service_changed;

btsig_error btsig_decode_service_changed(btsig_bytes input, const btsig_context* context, btsig_service_changed* value);

btsig_error btsig_encode_service_changed(const btsig_service_changed* value, uint8_t* out, size_t out_size,
                                         size_t* written);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_SERVICE_CHANGED_H
