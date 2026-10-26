#ifndef BTSIG_SCHEMA_DESCRIPTOR_HPP
#define BTSIG_SCHEMA_DESCRIPTOR_HPP

#include "btsig/types/status.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

constexpr std::uint8_t kSchemaVersion = 1;

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

struct FieldDescriptor {
    const char* name;
    const char* unit;
    std::size_t offset;
    std::int64_t raw_minimum;
    std::int64_t raw_maximum;
    const Sentinel* sentinels;
    std::size_t sentinel_count;
    btsig_value_kind value_kind;
    std::uint16_t unit_uuid;
    wire_type wire;
    std::int8_t coefficient;
    std::int8_t decimal_exponent;
    std::int8_t binary_exponent;
    // Octet maximum of a utf8 member. Zero for every other wire type.
    // The C member is uint16_t name_length followed by uint8_t name[utf8_capacity].
    std::uint16_t utf8_capacity;
    // Discrete codes for an enumeration member. Null unless allowed_count is non-zero.
    const std::int64_t* allowed;
    std::size_t allowed_count;
    // Bits that may be set on a flags member. Zero for every other field.
    std::uint64_t flag_mask;
};

struct CharacteristicDescriptor {
    const char* name;
    const char* id;
    std::uint16_t uuid;
    const char* unit;
    bool is_bitfield;
    std::size_t size;
    const FieldDescriptor* fields;
    std::size_t field_count;
};

} // namespace btsig

#endif
