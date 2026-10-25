#ifndef BTSIG_TYPES_SPAN_HPP
#define BTSIG_TYPES_SPAN_HPP

#include <cstddef>

namespace btsig {

template <typename T> class span {
  public:
    span(T* data, std::size_t size) : data_(data), size_(size) {}

    [[nodiscard]] T* data() const {
        return data_;
    }

    [[nodiscard]] std::size_t size() const {
        return size_;
    }

  private:
    T* data_;
    std::size_t size_;
};

} // namespace btsig

#endif
