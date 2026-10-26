// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/service_changed.h"

#include "btsig/codec/codec.h"

#include <stddef.h>

static const char service_changed_text[] = "service_changed\0"
                                           "org.bluetooth.characteristic.gatt.service_changed\0"
                                           "start_handle\0"
                                           "end_handle\0";

static const btsig_field_descriptor service_changed_fields[] = {
    {
        .raw_minimum = 0,
        .raw_maximum = 65535,
        .flag_mask = 0,
        .name_offset = 66,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_service_changed, start_handle),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 0,
        .utf8_capacity = 0,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_UINT16,
        .wire = BTSIG_WIRE_UINT16,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
    {
        .raw_minimum = 0,
        .raw_maximum = 65535,
        .flag_mask = 0,
        .name_offset = 79,
        .unit_offset = BTSIG_NO_TEXT,
        .offset = offsetof(btsig_service_changed, end_handle),
        .sentinel_offset = 0,
        .sentinel_count = 0,
        .allowed_offset = 0,
        .allowed_count = 0,
        .utf8_capacity = 0,
        .unit_uuid = 0,
        .value_kind = BTSIG_VALUE_UINT16,
        .wire = BTSIG_WIRE_UINT16,
        .coefficient = 1,
        .decimal_exponent = 0,
        .binary_exponent = 0,
    },
};

static const btsig_characteristic_descriptor service_changed_descriptor = {
    .text = service_changed_text,
    .sentinels = NULL,
    .allowed = NULL,
    .fields = service_changed_fields,
    .name_offset = 0,
    .id_offset = 16,
    .unit_offset = BTSIG_NO_TEXT,
    .uuid = 0x2A05,
    .size = sizeof(btsig_service_changed),
    .field_count = 2,
    .is_bitfield = 0,
};

btsig_error btsig_decode_service_changed(btsig_bytes input, const btsig_context* context,
                                         btsig_service_changed* value) {
    if (value == NULL) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig_codec_decode(&service_changed_descriptor, input, context, value, sizeof(*value));
}

btsig_error btsig_encode_service_changed(const btsig_service_changed* value, uint8_t* out, size_t out_size,
                                         size_t* written) {
    btsig_bytes empty = {0};
    if (value == NULL || written == NULL || (out == NULL && out_size != 0)) {
        btsig_error invalid = {0};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig_codec_encode(&service_changed_descriptor, value, sizeof(*value), out, out_size, written);
}

_Static_assert(sizeof(btsig_service_changed) == 4, "two uint16 handles");
_Static_assert(offsetof(btsig_service_changed, end_handle) == 2, "end handle follows start handle");
