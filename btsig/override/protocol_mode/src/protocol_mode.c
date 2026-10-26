// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/protocol_mode.h"

#include "btsig/codec/codec.h"

#include <stddef.h>

static const char protocol_mode_text[] = "protocol_mode\0"
                                         "org.bluetooth.characteristic.protocol_mode\0"
                                         "protocol_mode\0";

// HID Service 1.1, Table 2.2. 0x02 to 0xFF is reserved.
static const int64_t protocol_mode_allowed[] = {0, 1};

static const btsig_field_descriptor protocol_mode_fields[] = {
    {
        .raw_minimum = 0,
        .raw_maximum = 255,
        .flag_mask = 0,
        .name_offset = 57,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_protocol_mode, protocol_mode),
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
};

static const btsig_characteristic_descriptor protocol_mode_descriptor = {
    .text = protocol_mode_text,
    .sentinels = NULL,
    .allowed = protocol_mode_allowed,
    .fields = protocol_mode_fields,
    .name_offset = 0,
    .id_offset = 14,
    .unit_offset = BTSIG_NO_TEXT,
    .uuid = 0x2A4E,
    .size = sizeof(btsig_protocol_mode),
    .field_count = 1,
    .is_bitfield = 0,
};

btsig_error btsig_decode_protocol_mode(btsig_bytes input, const btsig_context* context, btsig_protocol_mode* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig_codec_decode(&protocol_mode_descriptor, input, context, value, sizeof(*value));
}

btsig_error btsig_encode_protocol_mode(const btsig_protocol_mode* value, uint8_t* out, size_t out_size,
                                       size_t* written) {
    btsig_bytes empty = {0};
    if (value == NULL || written == NULL || (out == NULL && out_size != 0)) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig_codec_encode(&protocol_mode_descriptor, value, sizeof(*value), out, out_size, written);
}

_Static_assert(sizeof(btsig_protocol_mode) == 4, "the public mode enum stays an int");
_Static_assert(sizeof(enum btsig_protocol_mode_value) == sizeof(int), "the public mode enum stays an int");
