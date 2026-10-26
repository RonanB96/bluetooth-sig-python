// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_SERVICE_CHANGED_HPP
#define BTSIG_SERVICE_CHANGED_HPP

#include "btsig/codec/codec.hpp"
#include "btsig/service_changed.h"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig {

class ServiceChanged {
  public:
    uint16_t start_handle;
    uint16_t end_handle;

    [[nodiscard]] static btsig::expected<ServiceChanged> decode(btsig_bytes input, const btsig_context* context);

    [[nodiscard]] static btsig::expected<std::size_t> encode(const ServiceChanged& value,
                                                             btsig::span<std::uint8_t> out);
};

extern const CharacteristicDescriptor service_changed_descriptor;

inline btsig::expected<ServiceChanged> ServiceChanged::decode(btsig_bytes input, const btsig_context* context) {
    ServiceChanged value{};
    const btsig_error error = btsig::decode(service_changed_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<ServiceChanged>(error);
    }
    return btsig::expected<ServiceChanged>(value);
}

inline btsig::expected<std::size_t> ServiceChanged::encode(const ServiceChanged& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(service_changed_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

#endif // BTSIG_SERVICE_CHANGED_HPP
