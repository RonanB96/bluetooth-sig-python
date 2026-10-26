#include "btsig/codec/codec.hpp"

#include "btsig/types/expected.hpp"
#include "btsig/wire/subbyte.hpp"
#include "btsig/wire/utf8.hpp"
#include "btsig/wire/word.hpp"

#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>

namespace btsig {
namespace {

constexpr std::size_t kStructScratchBytes = 512;
constexpr std::size_t kWireScratchBytes = 256;

btsig_error make_error(btsig_status status, const char* field, btsig_bytes bytes) {
    btsig_error error{};
    error.status = status;
    error.characteristic = nullptr;
    error.field = field;
    error.bytes = bytes;
    return error;
}

btsig_error annotate(btsig_error error, const char* field, btsig_bytes bytes) {
    error.characteristic = nullptr;
    error.field = field;
    error.bytes = bytes;
    return error;
}

struct MeasuredWire {
    std::size_t fixed_octets;
    bool utf8_tail;
    bool bit_packed;
    std::uint16_t utf8_capacity;
};

expected<MeasuredWire> measure_wire(const CharacteristicDescriptor& descriptor) {
    MeasuredWire measured{};
    if (descriptor.field_count != 0 && descriptor.fields == nullptr) {
        return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
    }
    std::size_t packed_bits = 0;
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const FieldDescriptor& field = descriptor.fields[index];
        const std::size_t bits = wire::bit_width(field.wire);
        if (bits != 0) {
            if (measured.utf8_tail || measured.fixed_octets != 0) {
                return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
            }
            measured.bit_packed = true;
            packed_bits += bits;
            continue;
        }
        if (measured.bit_packed) {
            return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
        }
        if (field.wire == wire_type::utf8) {
            // The UTF-8 value is the remaining octets, so it has to be the last field.
            if (measured.utf8_tail || index + 1 != descriptor.field_count || field.utf8_capacity == 0 ||
                field.utf8_capacity > kWireScratchBytes ||
                measured.fixed_octets > kWireScratchBytes - field.utf8_capacity) {
                return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
            }
            measured.utf8_tail = true;
            measured.utf8_capacity = field.utf8_capacity;
            continue;
        }
        const std::size_t field_width = wire::width(field.wire);
        if (field_width == 0 || measured.fixed_octets > kWireScratchBytes - field_width) {
            return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
        }
        measured.fixed_octets += field_width;
    }
    if (measured.bit_packed && (packed_bits == 0 || packed_bits % wire::kBitsPerOctet != 0 ||
                                packed_bits / wire::kBitsPerOctet > kWireScratchBytes)) {
        return unexpected_status<MeasuredWire>(BTSIG_INVALID_ARGUMENT);
    }
    if (measured.bit_packed) {
        measured.fixed_octets = packed_bits / wire::kBitsPerOctet;
    }
    return measured;
}

double apply_decimal(double value, std::int8_t exponent) {
    double decade = 1.0;
    if (exponent >= 0) {
        for (std::int8_t step = 0; step < exponent; ++step) {
            decade *= 10.0;
        }
        return value * decade;
    }
    for (std::int8_t step = exponent; step < 0; ++step) {
        decade *= 10.0;
    }
    return value / decade;
}

double apply_binary(double value, std::int8_t exponent) {
    if (exponent >= 0) {
        for (std::int8_t step = 0; step < exponent; ++step) {
            value *= 2.0;
        }
        return value;
    }
    for (std::int8_t step = exponent; step < 0; ++step) {
        value /= 2.0;
    }
    return value;
}

double scale_raw(std::int64_t raw, const FieldDescriptor& field) {
    const double coefficient = static_cast<double>(field.coefficient);
    return apply_binary(apply_decimal(static_cast<double>(raw) * coefficient, field.decimal_exponent),
                        field.binary_exponent);
}

double scale_factor(const FieldDescriptor& field) {
    return apply_binary(apply_decimal(static_cast<double>(field.coefficient), field.decimal_exponent),
                        field.binary_exponent);
}

const Sentinel* find_sentinel(const FieldDescriptor& field, std::int64_t raw) {
    if (field.sentinel_count != 0 && field.sentinels == nullptr) {
        return nullptr;
    }
    for (std::size_t index = 0; index < field.sentinel_count; ++index) {
        if (field.sentinels[index].raw_value == raw) {
            return &field.sentinels[index];
        }
    }
    return nullptr;
}

btsig_status sentinel_status(sentinel_meaning meaning) {
    if (meaning == sentinel_meaning::not_known) {
        return BTSIG_NOT_KNOWN;
    }
    return BTSIG_NOT_VALID;
}

bool in_range(std::int64_t raw, const FieldDescriptor& field) {
    return raw >= field.raw_minimum && raw <= field.raw_maximum;
}

bool value_accepted(std::int64_t raw, const FieldDescriptor& field) {
    if (!in_range(raw, field)) {
        return false;
    }
    if (field.flag_mask != 0) {
        if (raw < 0) {
            return false;
        }
        const auto bits = static_cast<std::uint64_t>(raw);
        return (bits & ~field.flag_mask) == 0U;
    }
    if (field.allowed_count == 0) {
        return true;
    }
    if (field.allowed == nullptr) {
        return false;
    }
    for (std::size_t index = 0; index < field.allowed_count; ++index) {
        if (field.allowed[index] == raw) {
            return true;
        }
    }
    return false;
}

std::size_t member_size(btsig_value_kind kind) {
    switch (kind) {
    case BTSIG_VALUE_UINT8:
        return sizeof(std::uint8_t);
    case BTSIG_VALUE_SINT8:
        return sizeof(std::int8_t);
    case BTSIG_VALUE_UINT16:
        return sizeof(std::uint16_t);
    case BTSIG_VALUE_SINT16:
        return sizeof(std::int16_t);
    case BTSIG_VALUE_UINT32:
        return sizeof(std::uint32_t);
    case BTSIG_VALUE_SINT32:
        return sizeof(std::int32_t);
    case BTSIG_VALUE_UINT64:
        return sizeof(std::uint64_t);
    case BTSIG_VALUE_DOUBLE:
        return sizeof(double);
    case BTSIG_VALUE_UTF8:
        return 0;
    }
    return 0;
}

std::size_t member_bytes(const FieldDescriptor& field) {
    if (field.wire == wire_type::utf8) {
        if (field.utf8_capacity == 0) {
            return 0;
        }
        return sizeof(std::uint16_t) + field.utf8_capacity;
    }
    return member_size(field.value_kind);
}

bool member_fits(const FieldDescriptor& field, std::size_t struct_size) {
    const std::size_t size = member_bytes(field);
    return size != 0 && field.offset <= struct_size && size <= struct_size - field.offset;
}

bool store_scaled(std::uint8_t* base, const FieldDescriptor& field, std::int64_t raw) {
    std::uint8_t* address = base + field.offset;
    switch (field.value_kind) {
    case BTSIG_VALUE_UINT8: {
        const auto stored = static_cast<std::uint8_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT16: {
        const auto stored = static_cast<std::uint16_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT32: {
        const auto stored = static_cast<std::uint32_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UINT64: {
        const auto stored = static_cast<std::uint64_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT8: {
        const auto stored = static_cast<std::int8_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT16: {
        const auto stored = static_cast<std::int16_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_SINT32: {
        const auto stored = static_cast<std::int32_t>(raw);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_DOUBLE: {
        const double stored = scale_raw(raw, field);
        std::memcpy(address, &stored, sizeof stored);
        return true;
    }
    case BTSIG_VALUE_UTF8:
        return false;
    }
    return false;
}

expected<std::int64_t> load_integer(const std::uint8_t* address, btsig_value_kind kind) {
    switch (kind) {
    case BTSIG_VALUE_UINT8: {
        std::uint8_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_UINT16: {
        std::uint16_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_UINT32: {
        std::uint32_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_UINT64: {
        std::uint64_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        if (stored > static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
            return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
        }
        return static_cast<std::int64_t>(stored);
    }
    case BTSIG_VALUE_SINT8: {
        std::int8_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_SINT16: {
        std::int16_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_SINT32: {
        std::int32_t stored = 0;
        std::memcpy(&stored, address, sizeof stored);
        return stored;
    }
    case BTSIG_VALUE_DOUBLE:
    case BTSIG_VALUE_UTF8:
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
}

expected<std::int64_t> raw_from_scaled(double member, const FieldDescriptor& field) {
    if (!std::isfinite(member)) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    const double factor = scale_factor(field);
    if (!std::isfinite(factor) || factor == 0.0) {
        return unexpected_status<std::int64_t>(BTSIG_INVALID_ARGUMENT);
    }
    const double quotient = member / factor;
    const double highest = static_cast<double>(std::numeric_limits<std::int64_t>::max());
    const double lowest = static_cast<double>(std::numeric_limits<std::int64_t>::min());
    if (!std::isfinite(quotient) || quotient >= highest || quotient < lowest) {
        return unexpected_status<std::int64_t>(BTSIG_OUT_OF_RANGE);
    }
    // std::llround rounds halfway cases away from zero (cppreference, std::round).
    return static_cast<std::int64_t>(std::llround(quotient));
}

} // namespace

btsig_error decode(const CharacteristicDescriptor& descriptor, btsig_bytes input, const btsig_context*, void* value,
                   std::size_t value_size) {
    if (value == nullptr || (input.data == nullptr && input.size != 0) || descriptor.size > kStructScratchBytes) {
        return make_error(BTSIG_INVALID_ARGUMENT, nullptr, input);
    }
    if (value_size < descriptor.size) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, nullptr, input);
    }
    const expected<MeasuredWire> measured = measure_wire(descriptor);
    if (!measured) {
        return annotate(measured.error(), nullptr, input);
    }
    if (input.size < measured.value().fixed_octets) {
        return make_error(BTSIG_INSUFFICIENT_DATA, nullptr, input);
    }
    if (!measured.value().utf8_tail && input.size != measured.value().fixed_octets) {
        return make_error(BTSIG_LENGTH_MISMATCH, nullptr, input);
    }
    if (measured.value().utf8_tail && input.size - measured.value().fixed_octets > measured.value().utf8_capacity) {
        return make_error(BTSIG_LENGTH_MISMATCH, nullptr, input);
    }

    // A failed field leaves the caller struct unchanged (ADR-0010).
    std::uint8_t scratch[kStructScratchBytes]{};
    std::size_t cursor = 0;
    std::size_t bit_cursor = 0;
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const FieldDescriptor& field = descriptor.fields[index];
        if (!member_fits(field, descriptor.size) || (field.sentinel_count != 0 && field.sentinels == nullptr) ||
            (field.allowed_count != 0 && field.allowed == nullptr)) {
            return make_error(BTSIG_INVALID_ARGUMENT, field.name, input);
        }
        if (field.wire == wire_type::utf8) {
            const std::size_t tail = input.size - cursor;
            const span<const std::uint8_t> text{tail == 0 ? nullptr : input.data + cursor, tail};
            const span<std::uint8_t> stored{scratch + field.offset + sizeof(std::uint16_t), field.utf8_capacity};
            const expected<std::size_t> copied = wire::read_utf8(text, stored);
            if (!copied) {
                return annotate(copied.error(), field.name, input);
            }
            const auto length = static_cast<std::uint16_t>(copied.value());
            std::memcpy(scratch + field.offset, &length, sizeof length);
            cursor += tail;
            continue;
        }
        const std::size_t bits = wire::bit_width(field.wire);
        const std::size_t field_width = bits == 0 ? wire::width(field.wire) : 0;
        const expected<std::int64_t> raw =
            bits == 0 ? wire::read(span<const std::uint8_t>{input.data + cursor, field_width}, field.wire)
                      : wire::read_bits(span<const std::uint8_t>{input.data, input.size}, bit_cursor, bits);
        if (!raw) {
            return annotate(raw.error(), field.name, input);
        }
        const Sentinel* sentinel = find_sentinel(field, raw.value());
        if (sentinel != nullptr) {
            return make_error(sentinel_status(sentinel->meaning), field.name, input);
        }
        if (!value_accepted(raw.value(), field)) {
            return make_error(BTSIG_OUT_OF_RANGE, field.name, input);
        }
        if (wire::is_real(field.wire)) {
            const expected<double> decoded = wire::decode_real(field.wire, raw.value());
            if (!decoded) {
                return annotate(decoded.error(), field.name, input);
            }
            std::memcpy(scratch + field.offset, &decoded.value(), sizeof decoded.value());
        } else if (!store_scaled(scratch, field, raw.value())) {
            return make_error(BTSIG_INVALID_ARGUMENT, field.name, input);
        }
        if (bits == 0) {
            cursor += field_width;
        } else {
            bit_cursor += bits;
        }
    }
    if (measured.value().bit_packed && bit_cursor != measured.value().fixed_octets * 8U) {
        return make_error(BTSIG_INVALID_ARGUMENT, nullptr, input);
    }
    std::memcpy(value, scratch, descriptor.size);
    return make_error(BTSIG_OK, nullptr, input);
}

btsig_error encode(const CharacteristicDescriptor& descriptor, const void* value, std::size_t value_size,
                   std::uint8_t* out, std::size_t out_size, std::size_t* written) {
    btsig_bytes buffer{out, out_size};
    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {
        return make_error(BTSIG_INVALID_ARGUMENT, nullptr, buffer);
    }
    if (value_size < descriptor.size) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, nullptr, buffer);
    }
    const expected<MeasuredWire> measured = measure_wire(descriptor);
    if (!measured) {
        return annotate(measured.error(), nullptr, buffer);
    }

    std::uint8_t scratch[kWireScratchBytes]{};
    const auto* base = static_cast<const std::uint8_t*>(value);
    std::size_t cursor = 0;
    std::size_t bit_cursor = 0;
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const FieldDescriptor& field = descriptor.fields[index];
        if (!member_fits(field, descriptor.size) || (field.allowed_count != 0 && field.allowed == nullptr)) {
            return make_error(BTSIG_INVALID_ARGUMENT, field.name, buffer);
        }
        if (field.wire == wire_type::utf8) {
            std::uint16_t length = 0;
            std::memcpy(&length, base + field.offset, sizeof length);
            if (length > field.utf8_capacity || length > kWireScratchBytes || cursor > kWireScratchBytes - length) {
                return make_error(length > field.utf8_capacity ? BTSIG_OUT_OF_RANGE : BTSIG_INVALID_ARGUMENT,
                                  field.name, buffer);
            }
            const span<const std::uint8_t> text{length == 0 ? nullptr : base + field.offset + sizeof(std::uint16_t),
                                                length};
            const btsig_error stored = wire::write_utf8(text, span<std::uint8_t>{scratch + cursor, length});
            if (stored.status != BTSIG_OK) {
                return annotate(stored, field.name, buffer);
            }
            cursor += length;
            continue;
        }
        const std::size_t bits = wire::bit_width(field.wire);
        const std::size_t field_width = bits == 0 ? wire::width(field.wire) : 0;
        const auto raw = [&]() -> expected<std::int64_t> {
            if (wire::is_real(field.wire)) {
                double member = 0.0;
                std::memcpy(&member, base + field.offset, sizeof member);
                return wire::encode_real(field.wire, member);
            }
            if (field.value_kind == BTSIG_VALUE_DOUBLE) {
                double member = 0.0;
                std::memcpy(&member, base + field.offset, sizeof member);
                return raw_from_scaled(member, field);
            }
            return load_integer(base + field.offset, field.value_kind);
        }();
        if (!raw) {
            return annotate(raw.error(), field.name, buffer);
        }
        if (!value_accepted(raw.value(), field)) {
            return make_error(BTSIG_OUT_OF_RANGE, field.name, buffer);
        }
        const btsig_error stored = bits == 0
                                       ? wire::write(span<std::uint8_t>{scratch + cursor, field_width}, raw.value())
                                       : wire::write_bits(span<std::uint8_t>{scratch, measured.value().fixed_octets},
                                                          bit_cursor, bits, raw.value());
        if (stored.status != BTSIG_OK) {
            return annotate(stored, field.name, buffer);
        }
        if (bits == 0) {
            cursor += field_width;
        } else {
            bit_cursor += bits;
        }
    }
    if (measured.value().bit_packed) {
        if (bit_cursor != measured.value().fixed_octets * 8U) {
            return make_error(BTSIG_INVALID_ARGUMENT, nullptr, buffer);
        }
        cursor = measured.value().fixed_octets;
    }
    if (out_size < cursor) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, nullptr, buffer);
    }
    if (!measured.value().utf8_tail && cursor != measured.value().fixed_octets) {
        return make_error(BTSIG_INVALID_ARGUMENT, nullptr, buffer);
    }
    if (out != nullptr && cursor != 0) {
        std::memcpy(out, scratch, cursor);
    }
    *written = cursor;
    buffer.size = cursor;
    return make_error(BTSIG_OK, nullptr, buffer);
}

} // namespace btsig
