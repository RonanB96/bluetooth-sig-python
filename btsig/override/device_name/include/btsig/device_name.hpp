// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_DEVICE_NAME_HPP
#define BTSIG_DEVICE_NAME_HPP

#include "btsig/codec/codec.hpp"
#include "btsig/device_name.h"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig {

class DeviceName {
  public:
    uint16_t device_name_length;
    uint8_t device_name[248];

    [[nodiscard]] static btsig::expected<DeviceName> decode(btsig_bytes input, const btsig_context* context);

    [[nodiscard]] static btsig::expected<std::size_t> encode(const DeviceName& value, btsig::span<std::uint8_t> out);
};

extern const CharacteristicDescriptor device_name_descriptor;

inline btsig::expected<DeviceName> DeviceName::decode(btsig_bytes input, const btsig_context* context) {
    DeviceName value{};
    const btsig_error error = btsig::decode(device_name_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<DeviceName>(error);
    }
    return btsig::expected<DeviceName>(value);
}

inline btsig::expected<std::size_t> DeviceName::encode(const DeviceName& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(device_name_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

#endif // BTSIG_DEVICE_NAME_HPP
