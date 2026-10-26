// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/protocol_mode.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace {

// HID Service 1.1, Table 2.2. 0x02 to 0xFF is reserved.
constexpr std::int64_t protocol_mode_allowed[] = {0, 1};

constexpr btsig::FieldDescriptor protocol_mode_fields[] = {
    {
        "protocol_mode",
        nullptr,
        offsetof(btsig_protocol_mode, protocol_mode),
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
        protocol_mode_allowed,
        2,
        0,
    },
};

} // namespace

extern const btsig::CharacteristicDescriptor protocol_mode_descriptor{
    "protocol_mode",
    "org.bluetooth.characteristic.protocol_mode",
    0x2A4E,
    nullptr,
    false,
    sizeof(btsig_protocol_mode),
    protocol_mode_fields,
    1,
};

extern "C" btsig_error btsig_decode_protocol_mode(btsig_bytes input, const btsig_context* context,
                                                  btsig_protocol_mode* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig::decode(protocol_mode_descriptor, input, context, value, sizeof(*value));
}

extern "C" btsig_error btsig_encode_protocol_mode(const btsig_protocol_mode* value, uint8_t* out, size_t out_size,
                                                  size_t* written) {
    btsig_bytes empty{nullptr, 0};
    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig::encode(protocol_mode_descriptor, value, sizeof(*value), out, out_size, written);
}

static_assert(btsig::kSchemaVersion == 1);
static_assert(std::is_standard_layout_v<btsig::ProtocolMode>);
static_assert(std::is_trivially_copyable_v<btsig::ProtocolMode>);
static_assert(sizeof(btsig_protocol_mode) == 4);
static_assert(sizeof(btsig::ProtocolMode) == sizeof(btsig_protocol_mode));
static_assert(sizeof(btsig_protocol_mode_value) == sizeof(int));
static_assert(sizeof(btsig::ProtocolModeValue) == sizeof(int));
