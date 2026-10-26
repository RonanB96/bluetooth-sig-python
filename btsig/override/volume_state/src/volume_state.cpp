// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/volume_state.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace {

constexpr char volume_state_text[] = "volume_state\0"
                                     "org.bluetooth.characteristic.volume_state\0"
                                     "volume_setting\0"
                                     "mute\0"
                                     "change_counter\0";

// Volume Control Service 1.0.1, section 2.3.1.2: Not Muted is 0 and Muted is 1.
constexpr std::int64_t volume_state_allowed[] = {0, 1};

constexpr btsig::FieldDescriptor volume_state_fields[] = {
    {
        0,
        255,
        0,
        55,
        btsig::kNoText,
        offsetof(btsig_volume_state, volume_setting),
        0,
        0,
        0,
        0,
        0,
        0,
        BTSIG_VALUE_UINT8,
        btsig::wire_type::uint8,
        1,
        0,
        0,
    },
    {
        0,
        255,
        0,
        70,
        btsig::kNoText,
        offsetof(btsig_volume_state, mute),
        0,
        0,
        0,
        2,
        0,
        0,
        BTSIG_VALUE_SINT32,
        btsig::wire_type::uint8,
        1,
        0,
        0,
    },
    {
        0,
        255,
        0,
        75,
        btsig::kNoText,
        offsetof(btsig_volume_state, change_counter),
        0,
        0,
        0,
        0,
        0,
        0,
        BTSIG_VALUE_UINT8,
        btsig::wire_type::uint8,
        1,
        0,
        0,
    },
};

} // namespace

extern const btsig::CharacteristicDescriptor volume_state_descriptor{
    volume_state_text,
    nullptr,
    volume_state_allowed,
    volume_state_fields,
    0,
    13,
    btsig::kNoText,
    0x2B7D,
    sizeof(btsig_volume_state),
    3,
    false,
};

extern "C" btsig_error btsig_decode_volume_state(btsig_bytes input, const btsig_context* context,
                                                 btsig_volume_state* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig::decode(volume_state_descriptor, input, context, value, sizeof(*value));
}

extern "C" btsig_error btsig_encode_volume_state(const btsig_volume_state* value, uint8_t* out, size_t out_size,
                                                 size_t* written) {
    btsig_bytes empty{nullptr, 0};
    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig::encode(volume_state_descriptor, value, sizeof(*value), out, out_size, written);
}

static_assert(btsig::kSchemaVersion == 1);
static_assert(std::is_standard_layout_v<btsig::VolumeState>);
static_assert(std::is_trivially_copyable_v<btsig::VolumeState>);
static_assert(sizeof(btsig_volume_state) == 12);
static_assert(sizeof(btsig::VolumeState) == sizeof(btsig_volume_state));
static_assert(offsetof(btsig_volume_state, mute) == 4);
static_assert(offsetof(btsig::VolumeState, mute) == 4);
static_assert(offsetof(btsig_volume_state, change_counter) == 8);
static_assert(offsetof(btsig::VolumeState, change_counter) == 8);
static_assert(sizeof(btsig_mute) == sizeof(int));
static_assert(sizeof(btsig::Mute) == sizeof(int));
