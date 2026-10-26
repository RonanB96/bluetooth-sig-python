#include "btsig/wire/utf8.h"

#include <stdbool.h>
#include <string.h>

static bool continuation(uint8_t byte) {
    return (byte & 0xC0U) == 0x80U;
}

// Lead byte, then continuation bounds. Overlong forms and values above U+10FFFF are rejected.
// ED encodes U+D000..U+DFFF, and the surrogate values in that range are well-formed.
static bool well_formed(const uint8_t* data, size_t size) {
    size_t index = 0;
    while (index < size) {
        const uint8_t lead = data[index];
        size_t width = 0;
        uint8_t minimum = 0x80U;
        uint8_t maximum = 0xBFU;
        if (lead <= 0x7FU) {
            index += 1U;
            continue;
        }
        if (lead >= 0xC2U && lead <= 0xDFU) {
            width = 2;
        } else if (lead == 0xE0U) {
            width = 3;
            minimum = 0xA0U;
        } else if (lead >= 0xE1U && lead <= 0xEFU) {
            // ED is in this range and keeps the default continuation bounds.
            width = 3;
        } else if (lead == 0xF0U) {
            width = 4;
            minimum = 0x90U;
        } else if (lead >= 0xF1U && lead <= 0xF3U) {
            width = 4;
        } else if (lead == 0xF4U) {
            width = 4;
            maximum = 0x8FU;
        } else {
            return false;
        }
        if (size - index < width) {
            return false;
        }
        const uint8_t second = data[index + 1U];
        if (second < minimum || second > maximum) {
            return false;
        }
        for (size_t extra = 2; extra < width; ++extra) {
            if (!continuation(data[index + extra])) {
                return false;
            }
        }
        index += width;
    }
    return true;
}

static bool null_with_size(const uint8_t* data, size_t size) {
    return size != 0 && data == NULL;
}

static btsig_status validated_copy(const uint8_t* data, size_t size, uint8_t* destination, size_t destination_size) {
    if (null_with_size(data, size) || null_with_size(destination, destination_size)) {
        return BTSIG_INVALID_ARGUMENT;
    }
    if (size > destination_size) {
        return BTSIG_LENGTH_MISMATCH;
    }
    if (!well_formed(data, size)) {
        return BTSIG_INVALID_ARGUMENT;
    }
    if (size != 0) {
        memcpy(destination, data, size);
    }
    return BTSIG_OK;
}

btsig_status btsig_wire_check_utf8(const uint8_t* data, size_t size) {
    if (null_with_size(data, size) || !well_formed(data, size)) {
        return BTSIG_INVALID_ARGUMENT;
    }
    return BTSIG_OK;
}

btsig_error btsig_wire_read_utf8(const uint8_t* data, size_t size, uint8_t* destination, size_t destination_size,
                                 size_t* copied) {
    btsig_error error = {0};
    if (copied == NULL) {
        error.status = BTSIG_INVALID_ARGUMENT;
        return error;
    }
    error.status = validated_copy(data, size, destination, destination_size);
    if (error.status == BTSIG_OK) {
        *copied = size;
    }
    return error;
}

btsig_error btsig_wire_write_utf8(const uint8_t* data, size_t size, uint8_t* out, size_t out_size) {
    btsig_error error = {0};
    error.status = validated_copy(data, size, out, out_size);
    return error;
}
