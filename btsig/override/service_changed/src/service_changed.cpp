// Handwritten override. This codec replaces a generated codec for the same characteristic id.

#include "btsig/service_changed.hpp"

#include "btsig/codec/codec.hpp"
#include "btsig/schema/descriptor.hpp"

#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace {

constexpr btsig::FieldDescriptor service_changed_fields[] = {
    {
        "start_handle",
        nullptr,
        offsetof(btsig_service_changed, start_handle),
        0,
        65535,
        nullptr,
        0,
        BTSIG_VALUE_UINT16,
        0,
        btsig::wire_type::uint16,
        1,
        0,
        0,
        0,
        nullptr,
        0,
        0,
    },
    {
        "end_handle",
        nullptr,
        offsetof(btsig_service_changed, end_handle),
        0,
        65535,
        nullptr,
        0,
        BTSIG_VALUE_UINT16,
        0,
        btsig::wire_type::uint16,
        1,
        0,
        0,
        0,
        nullptr,
        0,
        0,
    },
};

} // namespace

extern const btsig::CharacteristicDescriptor service_changed_descriptor{
    "service_changed",
    "org.bluetooth.characteristic.gatt.service_changed",
    0x2A05,
    nullptr,
    false,
    sizeof(btsig_service_changed),
    service_changed_fields,
    2,
};

extern "C" btsig_error btsig_decode_service_changed(btsig_bytes input, const btsig_context* context,
                                                    btsig_service_changed* value) {
    if (value == nullptr) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = input;
        return invalid;
    }
    return btsig::decode(service_changed_descriptor, input, context, value, sizeof(*value));
}

extern "C" btsig_error btsig_encode_service_changed(const btsig_service_changed* value, uint8_t* out, size_t out_size,
                                                    size_t* written) {
    btsig_bytes empty{nullptr, 0};
    if (value == nullptr || written == nullptr || (out == nullptr && out_size != 0)) {
        btsig_error invalid{};
        invalid.status = BTSIG_INVALID_ARGUMENT;
        invalid.bytes = empty;
        return invalid;
    }
    return btsig::encode(service_changed_descriptor, value, sizeof(*value), out, out_size, written);
}

static_assert(btsig::kSchemaVersion == 1);
static_assert(std::is_standard_layout_v<btsig::ServiceChanged>);
static_assert(std::is_trivially_copyable_v<btsig::ServiceChanged>);
static_assert(sizeof(btsig_service_changed) == 4);
static_assert(sizeof(btsig::ServiceChanged) == sizeof(btsig_service_changed));
static_assert(offsetof(btsig_service_changed, end_handle) == 2);
static_assert(offsetof(btsig::ServiceChanged, end_handle) == 2);
