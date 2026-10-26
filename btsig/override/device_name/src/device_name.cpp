// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/device_name.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace {

constexpr char device_name_text[] = "device_name\0"
                                    "org.bluetooth.characteristic.gap.device_name\0"
                                    "device_name\0";

constexpr btsig::FieldDescriptor device_name_fields[] = {
    {
        0,
        0,
        0,
        57,
        btsig::kNoText,
        offsetof(btsig_device_name, device_name_length),
        0,
        0,
        0,
        0,
        248,
        0,
        BTSIG_VALUE_UTF8,
        btsig::wire_type::utf8,
        1,
        0,
        0,
    },
};

} // namespace

extern const btsig::CharacteristicDescriptor device_name_descriptor{
    device_name_text,          nullptr, nullptr, device_name_fields, 0, 12, btsig::kNoText, 0x2A00,
    sizeof(btsig_device_name), 1,       false,
};

extern "C" btsig_error btsig_decode_device_name(btsig_bytes input, const btsig_context* context,
                                                btsig_device_name* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig::decode(device_name_descriptor, input, context, value, sizeof(*value));
}

extern "C" btsig_error btsig_encode_device_name(const btsig_device_name* value, uint8_t* out, size_t out_size,
                                                size_t* written) {
    btsig_bytes empty{nullptr, 0};
    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig::encode(device_name_descriptor, value, sizeof(*value), out, out_size, written);
}

static_assert(btsig::kSchemaVersion == 1);
static_assert(std::is_standard_layout_v<btsig::DeviceName>);
static_assert(std::is_trivially_copyable_v<btsig::DeviceName>);
static_assert(sizeof(btsig_device_name) == 250);
static_assert(sizeof(btsig::DeviceName) == sizeof(btsig_device_name));
static_assert(offsetof(btsig_device_name, device_name_length) == 0);
static_assert(offsetof(btsig::DeviceName, device_name_length) == 0);
