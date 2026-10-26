// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/volume_state.h"

#include "btsig/codec/codec.h"

#include <stddef.h>

static const char volume_state_text[] = "volume_state\0"
                                        "org.bluetooth.characteristic.volume_state\0"
                                        "volume_setting\0"
                                        "mute\0"
                                        "change_counter\0";

// Volume Control Service 1.0.1, section 2.3.1.2: Not Muted is 0 and Muted is 1.
static const int64_t volume_state_allowed[] = {0, 1};

static const btsig_field_descriptor volume_state_fields[] = {
    {
        .raw_minimum = 0,
        .raw_maximum = 255,
        .flag_mask = 0,
        .name_offset = 55,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_volume_state, volume_setting),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 0,
        .utf8_capacity = 0,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_UINT8,
        .wire = BTSIG_WIRE_UINT8,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
    {
        .raw_minimum = 0,
        .raw_maximum = 255,
        .flag_mask = 0,
        .name_offset = 70,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_volume_state, mute),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 2,
        .utf8_capacity = 0,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_SINT32,
        .wire = BTSIG_WIRE_UINT8,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
    {
        .raw_minimum = 0,
        .raw_maximum = 255,
        .flag_mask = 0,
        .name_offset = 75,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_volume_state, change_counter),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 0,
        .utf8_capacity = 0,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_UINT8,
        .wire = BTSIG_WIRE_UINT8,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
};

static const btsig_characteristic_descriptor volume_state_descriptor = {
    .text = volume_state_text,
    .sentinels = NULL,
    .allowed = volume_state_allowed,
    .fields = volume_state_fields,
    .name_offset = 0,
    .id_offset = 13,
    .unit_offset = BTSIG_NO_TEXT,
    .uuid = 0x2B7D,
    .size = sizeof(btsig_volume_state),
    .field_count = 3,
    .is_bitfield = 0,
};

btsig_error btsig_decode_volume_state(btsig_bytes input, const btsig_context* context, btsig_volume_state* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig_codec_decode(&volume_state_descriptor, input, context, value, sizeof(*value));
}

btsig_error btsig_encode_volume_state(const btsig_volume_state* value, uint8_t* out, size_t out_size, size_t* written) {
    btsig_bytes empty = {0};
    if (value == NULL || written == NULL || (out == NULL && out_size != 0)) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig_codec_encode(&volume_state_descriptor, value, sizeof(*value), out, out_size, written);
}

enum {
    volume_state_bytes = 12,
    change_counter_offset = 8,
};

_Static_assert(sizeof(btsig_volume_state) == volume_state_bytes, "volume state keeps the C enum width");
_Static_assert(offsetof(btsig_volume_state, mute) == 4, "mute follows the padded volume setting");
_Static_assert(offsetof(btsig_volume_state, change_counter) == change_counter_offset,
               "change counter follows the mute enum");
_Static_assert(sizeof(enum btsig_mute) == sizeof(int), "the public mute enum stays an int");
