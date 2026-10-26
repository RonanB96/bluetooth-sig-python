#include "btsig/codec/codec.h"

#include "btsig/types/utf8_text.h"
#include "btsig/wire/subbyte.h"
#include "btsig/wire/word.h"

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "real.h"

static btsig_error make_error(btsig_status status, const char* field, btsig_bytes bytes) {
    btsig_error error = {0};
    error.status = status;
    error.field = field;
    error.bytes = bytes;
    return error;
}

static btsig_error annotate(btsig_error error, const char* field, btsig_bytes bytes) {
    error.characteristic = NULL;
    error.field = field;
    error.bytes = bytes;
    return error;
}

typedef struct MeasuredWire {
    size_t fixed_octets;
    bool utf8_tail;
    bool bit_packed;
    uint16_t utf8_capacity;
} MeasuredWire;

static btsig_error measure_wire(const btsig_characteristic_descriptor* descriptor, MeasuredWire* measured) {
    *measured = (MeasuredWire){0};
    if (descriptor->field_count != 0 && descriptor->fields == NULL) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
    }
    size_t packed_bits = 0;
    for (size_t index = 0; index < descriptor->field_count; ++index) {
        const btsig_field_descriptor* field = &descriptor->fields[index];
        const size_t bits = btsig_wire_bit_width(field->wire);
        if (bits != 0) {
            if (measured->utf8_tail || measured->fixed_octets != 0) {
                return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
            }
            measured->bit_packed = true;
            packed_bits += bits;
            continue;
        }
        if (measured->bit_packed) {
            return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
        }
        if (field->wire == BTSIG_WIRE_UTF8) {
            // The UTF-8 value is the remaining octets, so it has to be the last field.
            if (measured->utf8_tail || index + 1 != descriptor->field_count || field->utf8_capacity == 0) {
                return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
            }
            measured->utf8_tail = true;
            measured->utf8_capacity = field->utf8_capacity;
            continue;
        }
        const size_t field_width = btsig_wire_width(field->wire);
        if (field_width == 0 || measured->fixed_octets > SIZE_MAX - field_width) {
            return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
        }
        measured->fixed_octets += field_width;
    }
    if (measured->bit_packed && (packed_bits == 0 || packed_bits % BTSIG_WIRE_BITS_PER_OCTET != 0)) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
    }
    if (measured->bit_packed) {
        measured->fixed_octets = packed_bits / BTSIG_WIRE_BITS_PER_OCTET;
    }
    return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
}

static const double decimal_radix = 10.0;
static const double binary_radix = 2.0;

static double apply_decimal(double value, int8_t exponent) {
    double decade = 1.0;
    if (exponent >= 0) {
        for (int8_t step = 0; step < exponent; ++step) {
            decade *= decimal_radix;
        }
        return value * decade;
    }
    for (int8_t step = exponent; step < 0; ++step) {
        decade *= decimal_radix;
    }
    return value / decade;
}

static double apply_binary(double value, int8_t exponent) {
    if (exponent >= 0) {
        for (int8_t step = 0; step < exponent; ++step) {
            value *= binary_radix;
        }
        return value;
    }
    for (int8_t step = exponent; step < 0; ++step) {
        value /= binary_radix;
    }
    return value;
}

static double scale_raw(int64_t raw, const btsig_field_descriptor* field) {
    const double coefficient = (double)field->coefficient;
    return apply_binary(apply_decimal((double)raw * coefficient, field->decimal_exponent), field->binary_exponent);
}

static double scale_factor(const btsig_field_descriptor* field) {
    return apply_binary(apply_decimal((double)field->coefficient, field->decimal_exponent), field->binary_exponent);
}

static const btsig_sentinel* find_sentinel(const btsig_sentinel* sentinels, uint16_t count, int64_t raw) {
    if (count != 0 && sentinels == NULL) {
        return NULL;
    }
    for (uint16_t index = 0; index < count; ++index) {
        if (sentinels[index].raw_value == raw) {
            return &sentinels[index];
        }
    }
    return NULL;
}

static btsig_status sentinel_status(uint8_t meaning) {
    if (meaning == BTSIG_SENTINEL_NOT_KNOWN) {
        return BTSIG_NOT_KNOWN;
    }
    return BTSIG_NOT_VALID;
}

static bool in_range(int64_t raw, const btsig_field_descriptor* field) {
    return raw >= field->raw_minimum && raw <= field->raw_maximum;
}

static bool value_accepted(int64_t raw, const btsig_field_descriptor* field, const int64_t* allowed) {
    if (!in_range(raw, field)) {
        return false;
    }
    if (field->flag_mask != 0) {
        if (raw < 0) {
            return false;
        }
        const uint64_t bits = (uint64_t)raw;
        return (bits & ~field->flag_mask) == 0U;
    }
    if (field->allowed_count == 0) {
        return true;
    }
    if (allowed == NULL) {
        return false;
    }
    for (uint16_t index = 0; index < field->allowed_count; ++index) {
        if (allowed[index] == raw) {
            return true;
        }
    }
    return false;
}

typedef struct FieldRefs {
    const char* name;
    const btsig_sentinel* sentinels;
    const int64_t* allowed;
} FieldRefs;

static FieldRefs field_refs(const btsig_characteristic_descriptor* descriptor, const btsig_field_descriptor* field) {
    FieldRefs refs = {0};
    if (descriptor->text != NULL) {
        refs.name = descriptor->text + field->name_offset;
    }
    if (field->sentinel_count != 0 && descriptor->sentinels != NULL) {
        refs.sentinels = descriptor->sentinels + field->sentinel_offset;
    }
    if (field->allowed_count != 0 && descriptor->allowed != NULL) {
        refs.allowed = descriptor->allowed + field->allowed_offset;
    }
    return refs;
}

static size_t member_size(btsig_value_kind kind) {
    switch (kind) {
    case BTSIG_VALUE_UINT8:
        return sizeof(uint8_t);
    case BTSIG_VALUE_SINT8:
        return sizeof(int8_t);
    case BTSIG_VALUE_UINT16:
        return sizeof(uint16_t);
    case BTSIG_VALUE_SINT16:
        return sizeof(int16_t);
    case BTSIG_VALUE_UINT32:
        return sizeof(uint32_t);
    case BTSIG_VALUE_SINT32:
        return sizeof(int32_t);
    case BTSIG_VALUE_UINT64:
        return sizeof(uint64_t);
    case BTSIG_VALUE_DOUBLE:
        return sizeof(double);
    case BTSIG_VALUE_UTF8:
        return 0;
    }
    return 0;
}

static size_t member_bytes(const btsig_field_descriptor* field) {
    if (field->wire == BTSIG_WIRE_UTF8) {
        if (field->utf8_capacity == 0) {
            return 0;
        }
        return btsig_stored_utf8_bytes(field->utf8_capacity);
    }
    return member_size(field->value_kind);
}

static bool member_fits(const btsig_field_descriptor* field, size_t struct_size) {
    const size_t size = member_bytes(field);
    return size != 0 && field->offset <= struct_size && size <= struct_size - field->offset;
}

static bool store_scaled(uint8_t* base, const btsig_field_descriptor* field, int64_t raw) {
    uint8_t* address = base + field->offset;
    switch (field->value_kind) {
    case BTSIG_VALUE_UINT8: {
        const uint8_t stored = (uint8_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT16: {
        const uint16_t stored = (uint16_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT32: {
        const uint32_t stored = (uint32_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT64: {
        const uint64_t stored = (uint64_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT8: {
        const int8_t stored = (int8_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT16: {
        const int16_t stored = (int16_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT32: {
        const int32_t stored = (int32_t)raw;
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_DOUBLE: {
        const double stored = scale_raw(raw, field);
        memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UTF8:
        return false;
    }
    return false;
}

static btsig_error load_integer(const uint8_t* address, btsig_value_kind kind, int64_t* raw) {
    switch (kind) {
    case BTSIG_VALUE_UINT8: {
        uint8_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_UINT16: {
        uint16_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_UINT32: {
        uint32_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_UINT64: {
        uint64_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        if (stored > (uint64_t)INT64_MAX) {
            return make_error(BTSIG_OUT_OF_RANGE, NULL, (btsig_bytes){0});
        }
        *raw = (int64_t)stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_SINT8: {
        int8_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_SINT16: {
        int16_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_SINT32: {
        int32_t stored = 0;
        memcpy(&stored, address, sizeof stored);
        *raw = stored;
        return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
    }
    case BTSIG_VALUE_DOUBLE:
    case BTSIG_VALUE_UTF8:
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
    }
    return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
}

static btsig_error raw_from_scaled(double member, const btsig_field_descriptor* field, int64_t* raw) {
    if (!isfinite(member)) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
    }
    const double factor = scale_factor(field);
    if (!isfinite(factor) || factor == 0.0) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, (btsig_bytes){0});
    }
    const double quotient = member / factor;
    const double highest = (double)INT64_MAX;
    const double lowest = (double)INT64_MIN;
    if (!isfinite(quotient) || quotient >= highest || quotient < lowest) {
        return make_error(BTSIG_OUT_OF_RANGE, NULL, (btsig_bytes){0});
    }
    // llround rounds halfway cases away from zero (C11 7.12.9.7).
    *raw = (int64_t)llround(quotient);
    return make_error(BTSIG_OK, NULL, (btsig_bytes){0});
}

static bool storable(const btsig_field_descriptor* field) {
    switch (field->value_kind) {
    case BTSIG_VALUE_UINT8:
    case BTSIG_VALUE_UINT16:
    case BTSIG_VALUE_UINT32:
    case BTSIG_VALUE_UINT64:
    case BTSIG_VALUE_SINT8:
    case BTSIG_VALUE_SINT16:
    case BTSIG_VALUE_SINT32:
    case BTSIG_VALUE_DOUBLE:
        return true;
    case BTSIG_VALUE_UTF8:
        return false;
    }
    return false;
}

static const uint8_t* at_offset(const uint8_t* data, size_t offset) {
    return data == NULL ? NULL : data + offset;
}

static uint8_t* at_mutable_offset(uint8_t* data, size_t offset) {
    return data == NULL ? NULL : data + offset;
}

static btsig_error read_raw(const uint8_t* data, size_t size, size_t cursor, size_t bit_cursor, size_t bits,
                            size_t field_width, uint8_t wire, int64_t* raw) {
    if (bits == 0) {
        return btsig_wire_read(at_offset(data, cursor), field_width, wire, raw);
    }
    return btsig_wire_read_bits(data, size, bit_cursor, bits, raw);
}

// Read the wire value without writing `value`. A non-OK status means the caller buffer stays unchanged.
static btsig_error accept_input(const btsig_characteristic_descriptor* descriptor, btsig_bytes input,
                                const MeasuredWire* measured) {
    size_t cursor = 0;
    size_t bit_cursor = 0;
    for (size_t index = 0; index < descriptor->field_count; ++index) {
        const btsig_field_descriptor* field = &descriptor->fields[index];
        const FieldRefs refs = field_refs(descriptor, field);
        if (!member_fits(field, descriptor->size) || (field->sentinel_count != 0 && refs.sentinels == NULL) ||
            (field->allowed_count != 0 && refs.allowed == NULL)) {
            return make_error(BTSIG_INVALID_ARGUMENT, refs.name, input);
        }
        if (field->wire == BTSIG_WIRE_UTF8) {
            cursor = input.size;
            continue;
        }
        const size_t bits = btsig_wire_bit_width(field->wire);
        const size_t field_width = bits == 0 ? btsig_wire_width(field->wire) : 0;
        int64_t raw = 0;
        const btsig_error error =
            read_raw(input.data, input.size, cursor, bit_cursor, bits, field_width, field->wire, &raw);
        if (error.status != BTSIG_OK) {
            return annotate(error, refs.name, input);
        }
        const btsig_sentinel* sentinel = find_sentinel(refs.sentinels, field->sentinel_count, raw);
        if (sentinel != NULL) {
            return make_error(sentinel_status(sentinel->meaning), refs.name, input);
        }
        if (!value_accepted(raw, field, refs.allowed)) {
            return make_error(BTSIG_OUT_OF_RANGE, refs.name, input);
        }
        if (btsig_wire_is_real(field->wire)) {
            double decoded = 0.0;
            const btsig_error decoded_error = btsig_wire_decode_real(field->wire, raw, &decoded);
            if (decoded_error.status != BTSIG_OK) {
                return annotate(decoded_error, refs.name, input);
            }
        } else if (!storable(field)) {
            return make_error(BTSIG_INVALID_ARGUMENT, refs.name, input);
        }
        if (bits == 0) {
            cursor += field_width;
        } else {
            bit_cursor += bits;
        }
    }
    if (measured->bit_packed && bit_cursor != measured->fixed_octets * BTSIG_WIRE_BITS_PER_OCTET) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, input);
    }
    return make_error(BTSIG_OK, NULL, input);
}

btsig_error btsig_codec_decode(const btsig_characteristic_descriptor* descriptor, btsig_bytes input,
                               const btsig_context* context, void* value, size_t value_size) {
    (void)context;
    if (descriptor == NULL || value == NULL || (input.data == NULL && input.size != 0)) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, input);
    }
    if (value_size < descriptor->size) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, NULL, input);
    }
    MeasuredWire measured = {0};
    const btsig_error measured_error = measure_wire(descriptor, &measured);
    if (measured_error.status != BTSIG_OK) {
        return annotate(measured_error, NULL, input);
    }
    if (input.size < measured.fixed_octets) {
        return make_error(BTSIG_INSUFFICIENT_DATA, NULL, input);
    }
    if (!measured.utf8_tail && input.size != measured.fixed_octets) {
        return make_error(BTSIG_LENGTH_MISMATCH, NULL, input);
    }
    if (measured.utf8_tail && input.size - measured.fixed_octets > measured.utf8_capacity) {
        return make_error(BTSIG_LENGTH_MISMATCH, NULL, input);
    }
    const btsig_error accepted = accept_input(descriptor, input, &measured);
    if (accepted.status != BTSIG_OK) {
        return accepted;
    }

    uint8_t* output = value;
    memset(output, 0, descriptor->size);
    size_t cursor = 0;
    size_t bit_cursor = 0;
    for (size_t index = 0; index < descriptor->field_count; ++index) {
        const btsig_field_descriptor* field = &descriptor->fields[index];
        const FieldRefs refs = field_refs(descriptor, field);
        if (!member_fits(field, descriptor->size) || (field->sentinel_count != 0 && refs.sentinels == NULL) ||
            (field->allowed_count != 0 && refs.allowed == NULL)) {
            return make_error(BTSIG_INVALID_ARGUMENT, refs.name, input);
        }
        if (field->wire == BTSIG_WIRE_UTF8) {
            const size_t tail = input.size - cursor;
            if (tail != 0) {
                memcpy(output + field->offset + sizeof(uint16_t), input.data + cursor, tail);
            }
            const uint16_t length = (uint16_t)tail;
            memcpy(output + field->offset, &length, sizeof length);
            cursor = input.size;
            continue;
        }
        const size_t bits = btsig_wire_bit_width(field->wire);
        const size_t field_width = bits == 0 ? btsig_wire_width(field->wire) : 0;
        int64_t raw = 0;
        const btsig_error error =
            read_raw(input.data, input.size, cursor, bit_cursor, bits, field_width, field->wire, &raw);
        if (error.status != BTSIG_OK) {
            return annotate(error, refs.name, input);
        }
        const btsig_sentinel* sentinel = find_sentinel(refs.sentinels, field->sentinel_count, raw);
        if (sentinel != NULL) {
            return make_error(sentinel_status(sentinel->meaning), refs.name, input);
        }
        if (!value_accepted(raw, field, refs.allowed)) {
            return make_error(BTSIG_OUT_OF_RANGE, refs.name, input);
        }
        if (btsig_wire_is_real(field->wire)) {
            double decoded = 0.0;
            const btsig_error decoded_error = btsig_wire_decode_real(field->wire, raw, &decoded);
            if (decoded_error.status != BTSIG_OK) {
                return annotate(decoded_error, refs.name, input);
            }
            memcpy(output + field->offset, &decoded, sizeof decoded);
        } else if (!store_scaled(output, field, raw)) {
            return make_error(BTSIG_INVALID_ARGUMENT, refs.name, input);
        }
        if (bits == 0) {
            cursor += field_width;
        } else {
            bit_cursor += bits;
        }
    }
    if (measured.bit_packed && bit_cursor != measured.fixed_octets * BTSIG_WIRE_BITS_PER_OCTET) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, input);
    }
    return make_error(BTSIG_OK, NULL, input);
}

btsig_error btsig_codec_encode(const btsig_characteristic_descriptor* descriptor, const void* value, size_t value_size,
                               uint8_t* out, size_t out_size, size_t* written) {
    btsig_bytes buffer = {out, out_size};
    if (descriptor == NULL || value == NULL || written == NULL || (out == NULL && out_size != 0)) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, buffer);
    }
    if (value_size < descriptor->size) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, NULL, buffer);
    }
    MeasuredWire measured = {0};
    const btsig_error measured_error = measure_wire(descriptor, &measured);
    if (measured_error.status != BTSIG_OK) {
        return annotate(measured_error, NULL, buffer);
    }

    if (measured.bit_packed) {
        if (out_size < measured.fixed_octets) {
            return make_error(BTSIG_BUFFER_TOO_SMALL, NULL, buffer);
        }
        // write_bits only sets bits that are present, so the caller's bytes start clear.
        // A zero-octet value is a null output with out_size 0, and memset rejects that pointer.
        if (measured.fixed_octets != 0) {
            memset(out, 0, measured.fixed_octets);
        }
    }
    const uint8_t* base = value;
    size_t cursor = 0;
    size_t bit_cursor = 0;
    for (size_t index = 0; index < descriptor->field_count; ++index) {
        const btsig_field_descriptor* field = &descriptor->fields[index];
        const FieldRefs refs = field_refs(descriptor, field);
        if (!member_fits(field, descriptor->size) || (field->allowed_count != 0 && refs.allowed == NULL)) {
            return make_error(BTSIG_INVALID_ARGUMENT, refs.name, buffer);
        }
        if (field->wire == BTSIG_WIRE_UTF8) {
            uint16_t length = 0;
            memcpy(&length, base + field->offset, sizeof length);
            if (length > field->utf8_capacity) {
                return make_error(BTSIG_OUT_OF_RANGE, refs.name, buffer);
            }
            if (cursor > out_size || length > out_size - cursor) {
                return make_error(BTSIG_BUFFER_TOO_SMALL, refs.name, buffer);
            }
            if (length != 0) {
                memcpy(out + cursor, base + field->offset + sizeof(uint16_t), length);
            }
            cursor += length;
            continue;
        }
        const size_t bits = btsig_wire_bit_width(field->wire);
        const size_t field_width = bits == 0 ? btsig_wire_width(field->wire) : 0;
        int64_t raw = 0;
        btsig_error raw_error = {0};
        if (btsig_wire_is_real(field->wire)) {
            double member = 0.0;
            memcpy(&member, base + field->offset, sizeof member);
            raw_error = btsig_wire_encode_real(field->wire, member, &raw);
        } else if (field->value_kind == BTSIG_VALUE_DOUBLE) {
            double member = 0.0;
            memcpy(&member, base + field->offset, sizeof member);
            raw_error = raw_from_scaled(member, field, &raw);
        } else {
            raw_error = load_integer(base + field->offset, field->value_kind, &raw);
        }
        if (raw_error.status != BTSIG_OK) {
            return annotate(raw_error, refs.name, buffer);
        }
        if (!value_accepted(raw, field, refs.allowed)) {
            return make_error(BTSIG_OUT_OF_RANGE, refs.name, buffer);
        }
        if (bits == 0 && (cursor > out_size || field_width > out_size - cursor)) {
            return make_error(BTSIG_BUFFER_TOO_SMALL, refs.name, buffer);
        }
        const btsig_error stored = bits == 0 ? btsig_wire_write(at_mutable_offset(out, cursor), field_width, raw)
                                             : btsig_wire_write_bits(out, measured.fixed_octets, bit_cursor, bits, raw);
        if (stored.status != BTSIG_OK) {
            return annotate(stored, refs.name, buffer);
        }
        if (bits == 0) {
            cursor += field_width;
        } else {
            bit_cursor += bits;
        }
    }
    if (measured.bit_packed) {
        if (bit_cursor != measured.fixed_octets * BTSIG_WIRE_BITS_PER_OCTET) {
            return make_error(BTSIG_INVALID_ARGUMENT, NULL, buffer);
        }
        cursor = measured.fixed_octets;
    }
    if (!measured.utf8_tail && cursor != measured.fixed_octets) {
        return make_error(BTSIG_INVALID_ARGUMENT, NULL, buffer);
    }
    *written = cursor;
    buffer.size = cursor;
    return make_error(BTSIG_OK, NULL, buffer);
}
