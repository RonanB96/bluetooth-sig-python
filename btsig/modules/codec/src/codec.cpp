#include "btsig/codec/codec.hpp"

#include "btsig/types/expected.hpp"
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

expected<std::size_t> total_wire_size(const CharacteristicDescriptor& descriptor) {
    std::size_t total = 0;
    if (descriptor.field_count != 0 && descriptor.fields == nullptr) {
        return unexpected_status<std::size_t>(BTSIG_INVALID_ARGUMENT);
    }
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const std::size_t field_width = wire::width(descriptor.fields[index].wire);
        if (field_width == 0 || total > kWireScratchBytes - field_width) {
            return unexpected_status<std::size_t>(BTSIG_INVALID_ARGUMENT);
        }
        total += field_width;
    }
    return total;
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
    }
    return 0;
}

bool member_fits(const FieldDescriptor& field, std::size_t struct_size) {
    const std::size_t size = member_size(field.value_kind);
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
    const expected<std::size_t> wire_size = total_wire_size(descriptor);
    if (!wire_size) {
        return annotate(wire_size.error(), nullptr, input);
    }
    if (input.size < wire_size.value()) {
        return make_error(BTSIG_INSUFFICIENT_DATA, nullptr, input);
    }
    if (input.size > wire_size.value()) {
        return make_error(BTSIG_LENGTH_MISMATCH, nullptr, input);
    }

    // A failed field leaves the caller struct unchanged (ADR-0010).
    std::uint8_t scratch[kStructScratchBytes]{};
    std::size_t cursor = 0;
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const FieldDescriptor& field = descriptor.fields[index];
        const std::size_t field_width = wire::width(field.wire);
        if (!member_fits(field, descriptor.size) || (field.sentinel_count != 0 && field.sentinels == nullptr)) {
            return make_error(BTSIG_INVALID_ARGUMENT, field.name, input);
        }
        const span<const std::uint8_t> word{input.data + cursor, field_width};
        const expected<std::int64_t> raw = wire::read(word, field.wire);
        if (!raw) {
            return annotate(raw.error(), field.name, input);
        }
        const Sentinel* sentinel = find_sentinel(field, raw.value());
        if (sentinel != nullptr) {
            return make_error(sentinel_status(sentinel->meaning), field.name, input);
        }
        if (!in_range(raw.value(), field)) {
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
        cursor += field_width;
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
    const expected<std::size_t> wire_size = total_wire_size(descriptor);
    if (!wire_size) {
        return annotate(wire_size.error(), nullptr, buffer);
    }
    if (out_size < wire_size.value()) {
        return make_error(BTSIG_BUFFER_TOO_SMALL, nullptr, buffer);
    }

    std::uint8_t scratch[kWireScratchBytes]{};
    const auto* base = static_cast<const std::uint8_t*>(value);
    std::size_t cursor = 0;
    for (std::size_t index = 0; index < descriptor.field_count; ++index) {
        const FieldDescriptor& field = descriptor.fields[index];
        const std::size_t field_width = wire::width(field.wire);
        if (!member_fits(field, descriptor.size)) {
            return make_error(BTSIG_INVALID_ARGUMENT, field.name, buffer);
        }
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
        if (!in_range(raw.value(), field)) {
            return make_error(BTSIG_OUT_OF_RANGE, field.name, buffer);
        }
        const btsig_error stored = wire::write(span<std::uint8_t>{scratch + cursor, field_width}, raw.value());
        if (stored.status != BTSIG_OK) {
            return annotate(stored, field.name, buffer);
        }
        cursor += field_width;
    }
    if (out != nullptr) {
        std::memcpy(out, scratch, wire_size.value());
    }
    *written = wire_size.value();
    buffer.size = wire_size.value();
    return make_error(BTSIG_OK, nullptr, buffer);
}

} // namespace btsig
