// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/device_name.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <type_traits>

namespace {

constexpr btsig::FieldDescriptor device_name_fields[] = {
    {
        "device_name",
        nullptr,
        offsetof(btsig_device_name, device_name_length),
        0,
        0,
        nullptr,
        0,
        BTSIG_VALUE_UTF8,
        0,
        btsig::wire_type::utf8,
        1,
        0,
        0,
        248,
        nullptr,
        0,
        0,
    },
};

constexpr btsig::CharacteristicDescriptor device_name_descriptor{
    "device_name",
    "org.bluetooth.characteristic.gap.device_name",
    0x2A00,
    nullptr,
    false,
    sizeof(btsig_device_name),
    device_name_fields,
    1,
};

} // namespace

namespace btsig {

btsig::expected<DeviceName> DeviceName::decode(btsig_bytes input, const btsig_context* context) {
    DeviceName value{};
    const btsig_error error = btsig::decode(device_name_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<DeviceName>(error);
    }
    return btsig::expected<DeviceName>(value);
}

btsig::expected<std::size_t> DeviceName::encode(const DeviceName& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(device_name_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

extern "C" btsig_error btsig_decode_device_name(btsig_bytes input, const btsig_context* context,
                                                btsig_device_name* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    const btsig::expected<btsig::DeviceName> decoded = btsig::DeviceName::decode(input, context);
    if (!decoded) {
        return decoded.error();
    }
    const btsig::DeviceName decoded_value = decoded.value();
    std::memcpy(value, &decoded_value, sizeof(*value));
    btsig_error ok{};
    ok.status = BTSIG_OK;
    ok.bytes = input;
    return ok;
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
    btsig::DeviceName typed{};
    std::memcpy(&typed, value, sizeof typed);
    const btsig::expected<std::size_t> encoded =
        btsig::DeviceName::encode(typed, btsig::span<std::uint8_t>(out, out_size));
    if (!encoded) {
        return encoded.error();
    }
    *written = encoded.value();
    btsig_error ok{};
    ok.status = BTSIG_OK;
    return ok;
}

static_assert(btsig::kSchemaVersion == 1);
static_assert(std::is_standard_layout_v<btsig::DeviceName>);
static_assert(std::is_trivially_copyable_v<btsig::DeviceName>);
static_assert(sizeof(btsig_device_name) == 250);
static_assert(sizeof(btsig::DeviceName) == sizeof(btsig_device_name));
static_assert(offsetof(btsig_device_name, device_name_length) == 0);
static_assert(offsetof(btsig::DeviceName, device_name_length) == 0);
