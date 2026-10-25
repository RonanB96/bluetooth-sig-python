#ifndef BTSIG_TYPES_EXPECTED_HPP
#define BTSIG_TYPES_EXPECTED_HPP

#include "btsig/types/status.h"

namespace btsig {

template <typename T> class unexpected {
  public:
    explicit unexpected(btsig_error error) : error_(error) {}

    [[nodiscard]] btsig_error error() const {
        return error_;
    }

  private:
    btsig_error error_;
};

template <typename T> class expected {
  public:
    expected(const T& value) : has_value_(true), value_(value), error_() {}

    expected(const unexpected<T>& error) : has_value_(false), value_(), error_(error.error()) {}

    [[nodiscard]] explicit operator bool() const {
        return has_value_;
    }

    [[nodiscard]] const T& value() const {
        return value_;
    }

    [[nodiscard]] btsig_error error() const {
        return error_;
    }

  private:
    bool has_value_;
    T value_;
    btsig_error error_;
};

} // namespace btsig

#endif
