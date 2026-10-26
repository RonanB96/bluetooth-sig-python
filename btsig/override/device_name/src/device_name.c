// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/device_name.h"

#include "btsig/codec/codec.h"

#include <stddef.h>

static const char device_name_text[] = "device_name\0"
                                       "org.bluetooth.characteristic.gap.device_name\0"
                                       "device_name\0";

static const btsig_field_descriptor device_name_fields[] = {
    {
        .raw_minimum = 0,
        .raw_maximum = 0,
        .flag_mask = 0,
        .name_offset = 57,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_device_name, device_name_length),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 0,
        .utf8_capacity = btsig_device_name_octets,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_UTF8,
        .wire = BTSIG_WIRE_UTF8,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
};

static const btsig_characteristic_descriptor device_name_descriptor = {
    .text = device_name_text,
    .sentinels = NULL,
    .allowed = NULL,
    .fields = device_name_fields,
    .name_offset = 0,
    .id_offset = 12,
    .unit_offset = BTSIG_NO_TEXT,
    .uuid = 0x2A00,
    .size = sizeof(btsig_device_name),
    .field_count = 1,
    .is_bitfield = 0,
};

btsig_error btsig_decode_device_name(btsig_bytes input, const btsig_context* context, btsig_device_name* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig_codec_decode(&device_name_descriptor, input, context, value, sizeof(*value));
}

btsig_error btsig_encode_device_name(const btsig_device_name* value, uint8_t* out, size_t out_size, size_t* written) {
    btsig_bytes empty = {0};
    if (value == NULL || written == NULL || (out == NULL && out_size != 0)) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig_codec_encode(&device_name_descriptor, value, sizeof(*value), out, out_size, written);
}

_Static_assert(sizeof(btsig_device_name) == sizeof(uint16_t) + btsig_device_name_octets, "length plus the name octets");
_Static_assert(offsetof(btsig_device_name, device_name_length) == 0, "the stored length is the first member");
