// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_VOLUME_STATE_HPP
#define BTSIG_VOLUME_STATE_HPP

#include "btsig/codec/codec.hpp"
#include "btsig/types/expected.hpp"
#include "btsig/types/span.hpp"
#include "btsig/volume_state.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

enum class Mute : int {
    not_muted = 0,
    muted = 1,
};

class VolumeState {
  public:
    uint8_t volume_setting;
    Mute mute;
    uint8_t change_counter;

    [[nodiscard]] static btsig::expected<VolumeState> decode(btsig_bytes input, const btsig_context* context);

    [[nodiscard]] static btsig::expected<std::size_t> encode(const VolumeState& value, btsig::span<std::uint8_t> out);
};

extern const CharacteristicDescriptor volume_state_descriptor;

inline btsig::expected<VolumeState> VolumeState::decode(btsig_bytes input, const btsig_context* context) {
    VolumeState value{};
    const btsig_error error = btsig::decode(volume_state_descriptor, input, context, &value, sizeof value);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<VolumeState>(error);
    }
    return btsig::expected<VolumeState>(value);
}

inline btsig::expected<std::size_t> VolumeState::encode(const VolumeState& value, btsig::span<std::uint8_t> out) {
    std::size_t written = 0;
    const btsig_error error =
        btsig::encode(volume_state_descriptor, &value, sizeof value, out.data(), out.size(), &written);
    if (error.status != BTSIG_OK) {
        return btsig::unexpected<std::size_t>(error);
    }
    return btsig::expected<std::size_t>(written);
}

} // namespace btsig

#endif // BTSIG_VOLUME_STATE_HPP
