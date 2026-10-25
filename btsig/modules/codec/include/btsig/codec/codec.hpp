#pragma once

#include "btsig/schema/descriptor.hpp"
#include "btsig/types/status.h"

#include <cstddef>
#include <cstdint>

namespace btsig {

[[nodiscard]] btsig_error decode(const CharacteristicDescriptor& descriptor, btsig_bytes input,
                                 const btsig_context* context, void* value, std::size_t value_size);

[[nodiscard]] btsig_error encode(const CharacteristicDescriptor& descriptor, const void* value, std::size_t value_size,
                                 std::uint8_t* out, std::size_t out_size, std::size_t* written);

} // namespace btsig
