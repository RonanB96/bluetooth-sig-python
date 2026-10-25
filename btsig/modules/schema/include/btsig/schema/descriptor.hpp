#pragma once

#include "btsig/types/status.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

constexpr int kSchemaVersion = 1;

enum class wire_type {
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
};

enum class sentinel_meaning { not_known, not_valid };

struct Sentinel {
    std::int64_t raw_value;
    sentinel_meaning meaning;
};

struct FieldDescriptor {
    const char* name;
    btsig_value_kind value_kind;
    const char* unit;
    std::uint16_t unit_uuid;
    std::size_t offset;
    wire_type wire;
    int coefficient;
    int decimal_exponent;
    int binary_exponent;
    std::int64_t raw_minimum;
    std::int64_t raw_maximum;
    const Sentinel* sentinels;
    std::size_t sentinel_count;
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
