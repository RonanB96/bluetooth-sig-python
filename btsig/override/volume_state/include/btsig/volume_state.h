// Handwritten override. This codec replaces a generated codec for the same characteristic id.
// Volume Control Service 1.0.1, Table 3.2: Volume_Setting, Mute, and Change_Counter, each uint8.
#ifndef BTSIG_VOLUME_STATE_H
#define BTSIG_VOLUME_STATE_H

#include "btsig/types/status.h"

#include <stddef.h>
#include <stdint.h>

enum btsig_mute {
    BTSIG_MUTE_NOT_MUTED = 0,
    BTSIG_MUTE_MUTED = 1,
};

#ifdef __cplusplus
extern "C" {
#endif

typedef struct btsig_volume_state {
    uint8_t volume_setting;
    enum btsig_mute mute;
    uint8_t change_counter;
} btsig_volume_state;

btsig_error btsig_decode_volume_state(btsig_bytes input, const btsig_context* context, btsig_volume_state* value);

btsig_error btsig_encode_volume_state(const btsig_volume_state* value, uint8_t* out, size_t out_size, size_t* written);

#ifdef __cplusplus
}
#endif

#endif // BTSIG_VOLUME_STATE_H
