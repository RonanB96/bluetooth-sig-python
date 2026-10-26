// Handwritten override. This codec replaces a generated codec for the same characteristic id.
// HID Service 1.1, Table 2.2: 0x00 Boot Protocol Mode, 0x01 Report Protocol Mode.
#ifndef BTSIG_PROTOCOL_MODE_H
#define BTSIG_PROTOCOL_MODE_H

#include "btsig/types/status.h"

#include <stddef.h>
#include <stdint.h>

enum btsig_protocol_mode_value {
    BTSIG_PROTOCOL_MODE_VALUE_BOOT_PROTOCOL_MODE = 0,
    BTSIG_PROTOCOL_MODE_VALUE_REPORT_PROTOCOL_MODE = 1,
};

#ifdef __cplusplus
extern "C" {
#endif

typedef struct btsig_protocol_mode {
    enum btsig_protocol_mode_value protocol_mode;
} btsig_protocol_mode;

btsig_error btsig_decode_protocol_mode(btsig_bytes input, const btsig_context* context, btsig_protocol_mode* value);

btsig_error btsig_encode_protocol_mode(const btsig_protocol_mode* value, uint8_t* out, size_t out_size,
                                       size_t* written);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_PROTOCOL_MODE_H
