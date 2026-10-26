// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_DEVICE_NAME_HPP
#define BTSIG_DEVICE_NAME_HPP

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

} // namespace btsig

#endif // BTSIG_DEVICE_NAME_HPP
