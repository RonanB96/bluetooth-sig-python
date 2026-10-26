#ifndef BTSIG_SCHEMA_DESCRIPTOR_HPP
#define BTSIG_SCHEMA_DESCRIPTOR_HPP

#include "btsig/schema/descriptor.h"
#include "btsig/types/status.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

constexpr std::uint8_t kSchemaVersion = BTSIG_SCHEMA_VERSION;

// Stored in a name or unit offset when that string is absent.
constexpr std::uint16_t kNoText = BTSIG_NO_TEXT;

enum class wire_type : std::uint8_t {
    uint8 = BTSIG_WIRE_UINT8,
    uint16 = BTSIG_WIRE_UINT16,
    uint24 = BTSIG_WIRE_UINT24,
    uint32 = BTSIG_WIRE_UINT32,
    uint48 = BTSIG_WIRE_UINT48,
    uint64 = BTSIG_WIRE_UINT64,
    sint8 = BTSIG_WIRE_SINT8,
    sint16 = BTSIG_WIRE_SINT16,
    sint24 = BTSIG_WIRE_SINT24,
    sint32 = BTSIG_WIRE_SINT32,
    boolean8 = BTSIG_WIRE_BOOLEAN8,
    boolean16 = BTSIG_WIRE_BOOLEAN16,
    boolean24 = BTSIG_WIRE_BOOLEAN24,
    boolean32 = BTSIG_WIRE_BOOLEAN32,
    medfloat16 = BTSIG_WIRE_MEDFLOAT16,
    medfloat32 = BTSIG_WIRE_MEDFLOAT32,
    float32 = BTSIG_WIRE_FLOAT32,
    utf8 = BTSIG_WIRE_UTF8,
    uint1 = BTSIG_WIRE_UINT1,
    uint2 = BTSIG_WIRE_UINT2,
};

enum class sentinel_meaning : std::uint8_t {
    not_known = BTSIG_SENTINEL_NOT_KNOWN,
    not_valid = BTSIG_SENTINEL_NOT_VALID,
};

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

static_assert(sizeof(Sentinel) == sizeof(btsig_sentinel), "Sentinel size");
static_assert(offsetof(Sentinel, raw_value) == offsetof(btsig_sentinel, raw_value), "Sentinel::raw_value");
static_assert(offsetof(Sentinel, meaning) == offsetof(btsig_sentinel, meaning), "Sentinel::meaning");

static_assert(sizeof(FieldDescriptor) == sizeof(btsig_field_descriptor), "FieldDescriptor size");
static_assert(offsetof(FieldDescriptor, raw_minimum) == offsetof(btsig_field_descriptor, raw_minimum),
              "FieldDescriptor::raw_minimum");
static_assert(offsetof(FieldDescriptor, raw_maximum) == offsetof(btsig_field_descriptor, raw_maximum),
              "FieldDescriptor::raw_maximum");
static_assert(offsetof(FieldDescriptor, flag_mask) == offsetof(btsig_field_descriptor, flag_mask),
              "FieldDescriptor::flag_mask");
static_assert(offsetof(FieldDescriptor, name_offset) == offsetof(btsig_field_descriptor, name_offset),
              "FieldDescriptor::name_offset");
static_assert(offsetof(FieldDescriptor, unit_offset) == offsetof(btsig_field_descriptor, unit_offset),
              "FieldDescriptor::unit_offset");
static_assert(offsetof(FieldDescriptor, offset) == offsetof(btsig_field_descriptor, offset), "FieldDescriptor::offset");
static_assert(offsetof(FieldDescriptor, sentinel_offset) == offsetof(btsig_field_descriptor, sentinel_offset),
              "FieldDescriptor::sentinel_offset");
static_assert(offsetof(FieldDescriptor, sentinel_count) == offsetof(btsig_field_descriptor, sentinel_count),
              "FieldDescriptor::sentinel_count");
static_assert(offsetof(FieldDescriptor, allowed_offset) == offsetof(btsig_field_descriptor, allowed_offset),
              "FieldDescriptor::allowed_offset");
static_assert(offsetof(FieldDescriptor, allowed_count) == offsetof(btsig_field_descriptor, allowed_count),
              "FieldDescriptor::allowed_count");
static_assert(offsetof(FieldDescriptor, utf8_capacity) == offsetof(btsig_field_descriptor, utf8_capacity),
              "FieldDescriptor::utf8_capacity");
static_assert(offsetof(FieldDescriptor, unit_uuid) == offsetof(btsig_field_descriptor, unit_uuid),
              "FieldDescriptor::unit_uuid");
static_assert(offsetof(FieldDescriptor, value_kind) == offsetof(btsig_field_descriptor, value_kind),
              "FieldDescriptor::value_kind");
static_assert(offsetof(FieldDescriptor, wire) == offsetof(btsig_field_descriptor, wire), "FieldDescriptor::wire");
static_assert(offsetof(FieldDescriptor, coefficient) == offsetof(btsig_field_descriptor, coefficient),
              "FieldDescriptor::coefficient");
static_assert(offsetof(FieldDescriptor, decimal_exponent) == offsetof(btsig_field_descriptor, decimal_exponent),
              "FieldDescriptor::decimal_exponent");
static_assert(offsetof(FieldDescriptor, binary_exponent) == offsetof(btsig_field_descriptor, binary_exponent),
              "FieldDescriptor::binary_exponent");

static_assert(sizeof(CharacteristicDescriptor) == sizeof(btsig_characteristic_descriptor),
              "CharacteristicDescriptor size");
static_assert(offsetof(CharacteristicDescriptor, text) == offsetof(btsig_characteristic_descriptor, text),
              "CharacteristicDescriptor::text");
static_assert(offsetof(CharacteristicDescriptor, sentinels) == offsetof(btsig_characteristic_descriptor, sentinels),
              "CharacteristicDescriptor::sentinels");
static_assert(offsetof(CharacteristicDescriptor, allowed) == offsetof(btsig_characteristic_descriptor, allowed),
              "CharacteristicDescriptor::allowed");
static_assert(offsetof(CharacteristicDescriptor, fields) == offsetof(btsig_characteristic_descriptor, fields),
              "CharacteristicDescriptor::fields");
static_assert(offsetof(CharacteristicDescriptor, name_offset) == offsetof(btsig_characteristic_descriptor, name_offset),
              "CharacteristicDescriptor::name_offset");
static_assert(offsetof(CharacteristicDescriptor, id_offset) == offsetof(btsig_characteristic_descriptor, id_offset),
              "CharacteristicDescriptor::id_offset");
static_assert(offsetof(CharacteristicDescriptor, unit_offset) == offsetof(btsig_characteristic_descriptor, unit_offset),
              "CharacteristicDescriptor::unit_offset");
static_assert(offsetof(CharacteristicDescriptor, uuid) == offsetof(btsig_characteristic_descriptor, uuid),
              "CharacteristicDescriptor::uuid");
static_assert(offsetof(CharacteristicDescriptor, size) == offsetof(btsig_characteristic_descriptor, size),
              "CharacteristicDescriptor::size");
static_assert(offsetof(CharacteristicDescriptor, field_count) == offsetof(btsig_characteristic_descriptor, field_count),
              "CharacteristicDescriptor::field_count");
static_assert(offsetof(CharacteristicDescriptor, is_bitfield) == offsetof(btsig_characteristic_descriptor, is_bitfield),
              "CharacteristicDescriptor::is_bitfield");

} // namespace btsig

#endif
