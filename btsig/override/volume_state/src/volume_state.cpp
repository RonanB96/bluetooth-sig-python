// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/volume_state.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <type_traits>

namespace {

// Volume Control Service 1.0.1, section 2.3.1.2: Not Muted is 0 and Muted is 1.
constexpr std::int64_t volume_state_mute_allowed[] = {0, 1};

constexpr btsig::FieldDescriptor volume_state_fields[] = {
    {
        "volume_setting",
        nullptr,
        offsetof(btsig_volume_state, volume_setting),
        0,
        255,
        nullptr,
        0,
        BTSIG_VALUE_UINT8,
        0,
        btsig::wire_type::uint8,
        1,
        0,
        0,
        0,
        nullptr,
        0,
        0,
    },
    {
        "mute",
        nullptr,
        offsetof(btsig_volume_state, mute),
        0,
        255,
        nullptr,
        0,
        BTSIG_VALUE_SINT32,
        0,
        btsig::wire_type::uint8,
        1,
        0,
        0,
        0,
        volume_state_mute_allowed,
        2,
        0,
    },
    {
        "change_counter",
        nullptr,
        offsetof(btsig_volume_state, change_counter),
        0,
        255,
        nullptr,
        0,
        BTSIG_VALUE_UINT8,
        0,
        btsig::wire_type::uint8,
        1,
        0,
        0,
        0,
        nullptr,
        0,
        0,
    },
};

constexpr btsig::CharacteristicDescriptor volume_state_descriptor{
    "volume_state",
    "org.bluetooth.characteristic.volume_state",
    0x2B7D,
    nullptr,
    false,
    sizeof(btsig_volume_state),
    volume_state_fields,
    3,
};

} // namespace

namespace btsig {

btsig::expected<VolumeState> VolumeState::decode(btsig_bytes input, const btsig_context* context) {
    VolumeState value{};
    const btsig_error error = btsig::decode(volume_state_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<VolumeState>(error);
    }
    return btsig::expected<VolumeState>(value);
}

btsig::expected<std::size_t> VolumeState::encode(const VolumeState& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(volume_state_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

extern "C" btsig_error btsig_decode_volume_state(btsig_bytes input, const btsig_context* context,
                                                 btsig_volume_state* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    const btsig::expected<btsig::VolumeState> decoded = btsig::VolumeState::decode(input, context);
    if (!decoded) {
        return decoded.error();
    }
    const btsig::VolumeState decoded_value = decoded.value();
    std::memcpy(value, &decoded_value, sizeof(*value));
    btsig_error ok{};
    ok.status = BTSIG_OK;
    ok.bytes = input;
    return ok;
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
    btsig::VolumeState typed{};
    std::memcpy(&typed, value, sizeof typed);
    const btsig::expected<std::size_t> encoded =
        btsig::VolumeState::encode(typed, btsig::span<std::uint8_t>(out, out_size));
    if (!encoded) {
        return encoded.error();
    }
    *written = encoded.value();
    btsig_error ok{};
    ok.status = BTSIG_OK;
    return ok;
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
