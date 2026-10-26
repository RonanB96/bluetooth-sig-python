// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_PROTOCOL_MODE_HPP
#define BTSIG_PROTOCOL_MODE_HPP

#include "btsig/codec/codec.hpp"
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

extern const CharacteristicDescriptor protocol_mode_descriptor;

inline btsig::expected<ProtocolMode> ProtocolMode::decode(btsig_bytes input, const btsig_context* context) {
    ProtocolMode value{};
    const btsig_error error = btsig::decode(protocol_mode_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<ProtocolMode>(error);
    }
    return btsig::expected<ProtocolMode>(value);
}

inline btsig::expected<std::size_t> ProtocolMode::encode(const ProtocolMode& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(protocol_mode_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

#endif // BTSIG_PROTOCOL_MODE_HPP
