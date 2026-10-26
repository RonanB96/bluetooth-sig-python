// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_PROTOCOL_MODE_HPP
#define BTSIG_PROTOCOL_MODE_HPP

#include "btsig/protocol_mode.h"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"

#include <cstddef>
#include <cstdint>

namespace btsig {

enum class ProtocolModeValue : int {
    boot_protocol_mode = 0,
    report_protocol_mode = 1,
};

class ProtocolMode {
  public:
    ProtocolModeValue protocol_mode;

    [[nodiscard]] static btsig::expected<ProtocolMode> decode(btsig_bytes input, const btsig_context* context);

    [[nodiscard]] static btsig::expected<std::size_t> encode(const ProtocolMode& value, btsig::span<std::uint8_t> out);
};

} // namespace btsig

#endif // BTSIG_PROTOCOL_MODE_HPP
