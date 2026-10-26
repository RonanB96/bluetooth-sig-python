#ifndef BTSIG_SCHEMA_DESCRIPTOR_HPP
#define BTSIG_SCHEMA_DESCRIPTOR_HPP

#include "btsig/types/status.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

constexpr std::uint8_t kSchemaVersion = 1;

// Stored in a name or unit offset when that string is absent.
constexpr std::uint16_t kNoText = 0xFFFF;

enum class wire_type : std::uint8_t {
    uint8,
    uint16,
    uint24,
    uint32,
    uint48,
    uint64,
    sint8,
    sint16,
    sint24,
    sint32,
    boolean8,
    boolean16,
    boolean24,
    boolean32,
    medfloat16,
    medfloat32,
    float32,
    utf8,
    uint1,
    uint2,
};

enum class sentinel_meaning : std::uint8_t { not_known, not_valid };

struct Sentinel {
    std::int64_t raw_value;
    sentinel_meaning meaning;
};

// No pointers. A field table can stay in flash. Strings, sentinels, and allowed
// values are addressed from the characteristic descriptor that owns this field.
struct FieldDescriptor {
    std::int64_t raw_minimum;
    std::int64_t raw_maximum;
    // Bits that may be set on a flags member. Zero for every other field.
    std::uint64_t flag_mask;
    std::uint16_t name_offset;
    std::uint16_t unit_offset;
    std::uint16_t offset;
    std::uint16_t sentinel_offset;
    std::uint16_t sentinel_count;
    std::uint16_t allowed_offset;
    std::uint16_t allowed_count;
    // Octet maximum of a utf8 member. Zero for every other wire type.
    // The member starts at `offset`: uint16_t size, then uint8_t data[utf8_capacity].
    std::uint16_t utf8_capacity;
    std::uint16_t unit_uuid;
    btsig_value_kind value_kind;
    wire_type wire;
    std::int8_t coefficient;
    std::int8_t decimal_exponent;
    std::int8_t binary_exponent;
};

struct CharacteristicDescriptor {
    const char* text;
    const Sentinel* sentinels;
    const std::int64_t* allowed;
    const FieldDescriptor* fields;
    std::uint16_t name_offset;
    std::uint16_t id_offset;
    std::uint16_t unit_offset;
    std::uint16_t uuid;
    std::uint16_t size;
    std::uint16_t field_count;
    bool is_bitfield;
};

} // namespace btsig

#endif
