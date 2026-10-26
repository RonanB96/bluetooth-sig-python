#ifndef BTSIG_TYPES_UTF8_TEXT_H
#define BTSIG_TYPES_UTF8_TEXT_H

#include <stddef.h>
#include <stdint.h>

// `uint16_t size` plus `uint8_t data[capacity]`, rounded up to a multiple of `sizeof(uint16_t)`.
// `constexpr` in C++ so `stored_utf8_bytes` can use this in a constant expression.
#ifdef __cplusplus
#define BTSIG_STORED_UTF8_BYTES_CONSTEXPR constexpr
#else
#define BTSIG_STORED_UTF8_BYTES_CONSTEXPR
#endif

static inline BTSIG_STORED_UTF8_BYTES_CONSTEXPR size_t btsig_stored_utf8_bytes(uint16_t capacity) {
    const size_t raw = sizeof(uint16_t) + capacity;
    const size_t alignment = sizeof(uint16_t);
    return (raw + alignment - 1) / alignment * alignment;
}

#undef BTSIG_STORED_UTF8_BYTES_CONSTEXPR

#endif
