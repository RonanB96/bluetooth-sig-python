// Handwritten override. This codec replaces a generated codec for the same characteristic id.
#ifndef BTSIG_VOLUME_STATE_HPP
#define BTSIG_VOLUME_STATE_HPP

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

} // namespace btsig

#endif // BTSIG_VOLUME_STATE_HPP
