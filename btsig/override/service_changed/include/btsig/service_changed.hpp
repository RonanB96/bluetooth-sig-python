// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_SERVICE_CHANGED_HPP
#define BTSIG_SERVICE_CHANGED_HPP

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

} // namespace btsig

#endif // BTSIG_SERVICE_CHANGED_HPP
