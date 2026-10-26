#ifndef BTSIG_TYPES_UTF8_TEXT_H
#define BTSIG_TYPES_UTF8_TEXT_H

#include <stddef.h>
#include <stdint.h>

// `uint16_t size` plus `uint8_t data[capacity]`, rounded up to a multiple of `sizeof(uint16_t)`.
static inline size_t btsig_stored_utf8_bytes(uint16_t capacity) {
    const size_t raw = sizeof(uint16_t) + capacity;
    const size_t alignment = sizeof(uint16_t);
    return (raw + alignment - 1) / alignment * alignment;
}

#endif
