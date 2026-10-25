#include "btsig/battery_level.hpp"
#include "btsig/electric_current_statistics.hpp"
#include "btsig/temperature.hpp"
#include "btsig/temperature_range.hpp"

#include <cstdio>
#include <cstring>

namespace {

const char *status_name(btsig_status status) {
  switch (status) {
  case BTSIG_OK:
    return "BTSIG_OK";
  case BTSIG_INSUFFICIENT_DATA:
    return "BTSIG_INSUFFICIENT_DATA";
  case BTSIG_LENGTH_MISMATCH:
    return "BTSIG_LENGTH_MISMATCH";
  case BTSIG_UNKNOWN_UUID:
    return "BTSIG_UNKNOWN_UUID";
  case BTSIG_OUT_OF_RANGE:
    return "BTSIG_OUT_OF_RANGE";
  case BTSIG_BUFFER_TOO_SMALL:
    return "BTSIG_BUFFER_TOO_SMALL";
  case BTSIG_INVALID_ARGUMENT:
    return "BTSIG_INVALID_ARGUMENT";
  case BTSIG_NOT_KNOWN:
    return "BTSIG_NOT_KNOWN";
  case BTSIG_NOT_VALID:
    return "BTSIG_NOT_VALID";
  }
  return "BTSIG_STATUS";
}

void print_failure(const char *call, btsig_error error) {
  const char *field = error.field == nullptr ? "-" : error.field;
  std::printf("  %s -> %s field=%s\n", call, status_name(error.status), field);
}

void print_bytes(const char *label, const std::uint8_t *data,
                 std::size_t size) {
  std::printf("  %s (%zu)", label, size);
  for (std::size_t index = 0; index < size; ++index) {
    std::printf(" %02X", data[index]);
  }
  std::printf("\n");
}

bool same_bytes(const std::uint8_t *left, std::size_t left_size,
                const std::uint8_t *right, std::size_t right_size) {
  return left_size == right_size && std::memcmp(left, right, left_size) == 0;
}

bool battery_level() {
  const std::uint8_t wire[] = {0x64};
  const btsig_bytes input{wire, sizeof wire};
  std::printf("BatteryLevel::decode / encode\n");
  const btsig::expected<btsig::BatteryLevel> decoded =
      btsig::BatteryLevel::decode(input, nullptr);
  if (!decoded) {
    print_failure("decode", decoded.error());
    return false;
  }
  const btsig::BatteryLevel value = decoded.value();
  std::printf("  battery_level = %u\n", value.battery_level);

  std::uint8_t encoded_bytes[4]{};
  const btsig::expected<std::size_t> encoded = btsig::BatteryLevel::encode(
      value, btsig::span<std::uint8_t>(encoded_bytes, sizeof encoded_bytes));
  if (!encoded) {
    print_failure("encode", encoded.error());
    return false;
  }
  print_bytes("encoded", encoded_bytes, encoded.value());
  return value.battery_level == 100 &&
         same_bytes(encoded_bytes, encoded.value(), wire, sizeof wire);
}

bool temperature() {
  const std::uint8_t wire[] = {0x08, 0x07};
  const btsig_bytes input{wire, sizeof wire};
  std::printf("Temperature::decode / encode\n");
  const btsig::expected<btsig::Temperature> decoded =
      btsig::Temperature::decode(input, nullptr);
  if (!decoded) {
    print_failure("decode", decoded.error());
    return false;
  }
  const btsig::Temperature value = decoded.value();
  std::printf("  temperature = %.2f C\n", value.temperature);

  std::uint8_t encoded_bytes[8]{};
  const btsig::expected<std::size_t> encoded = btsig::Temperature::encode(
      value, btsig::span<std::uint8_t>(encoded_bytes, sizeof encoded_bytes));
  if (!encoded) {
    print_failure("encode", encoded.error());
    return false;
  }
  print_bytes("encoded", encoded_bytes, encoded.value());
  return value.temperature == 18.0 &&
         same_bytes(encoded_bytes, encoded.value(), wire, sizeof wire);
}

bool temperature_not_known() {
  const std::uint8_t wire[] = {0x00, 0x80};
  const btsig_bytes input{wire, sizeof wire};
  std::printf("Temperature::decode sentinel\n");
  const btsig::expected<btsig::Temperature> decoded =
      btsig::Temperature::decode(input, nullptr);
  if (decoded) {
    std::printf("  decode -> BTSIG_OK\n");
    return false;
  }
  print_failure("decode", decoded.error());
  return decoded.error().status == BTSIG_NOT_KNOWN &&
         decoded.error().field != nullptr;
}

bool temperature_range() {
  const std::uint8_t wire[] = {0x08, 0x07, 0xF0, 0x0A};
  const btsig_bytes input{wire, sizeof wire};
  std::printf("TemperatureRange::decode / encode\n");
  const btsig::expected<btsig::TemperatureRange> decoded =
      btsig::TemperatureRange::decode(input, nullptr);
  if (!decoded) {
    print_failure("decode", decoded.error());
    return false;
  }
  const btsig::TemperatureRange value = decoded.value();
  std::printf("  minimum = %.2f C, maximum = %.2f C\n", value.minimum,
              value.maximum);

  std::uint8_t encoded_bytes[8]{};
  const btsig::expected<std::size_t> encoded = btsig::TemperatureRange::encode(
      value, btsig::span<std::uint8_t>(encoded_bytes, sizeof encoded_bytes));
  if (!encoded) {
    print_failure("encode", encoded.error());
    return false;
  }
  print_bytes("encoded", encoded_bytes, encoded.value());
  return value.minimum == 18.0 && value.maximum == 28.0 &&
         same_bytes(encoded_bytes, encoded.value(), wire, sizeof wire);
}

bool electric_current_statistics() {
  const std::uint8_t wire[] = {0x96, 0x00, 0x32, 0x00, 0x64,
                               0x00, 0xC8, 0x00, 0x1E};
  const btsig_bytes input{wire, sizeof wire};
  std::printf("ElectricCurrentStatistics::decode / encode\n");
  const btsig::expected<btsig::ElectricCurrentStatistics> decoded =
      btsig::ElectricCurrentStatistics::decode(input, nullptr);
  if (!decoded) {
    print_failure("decode", decoded.error());
    return false;
  }
  const btsig::ElectricCurrentStatistics value = decoded.value();
  std::printf("  average = %.2f A, standard_deviation = %.2f A, minimum = %.2f "
              "A, maximum = %.2f A, duration = %u s\n",
              value.average_electric_current_value,
              value.standard_deviation_electric_current_value,
              value.minimum_electric_current_value,
              value.maximum_electric_current_value, value.sensing_duration);

  std::uint8_t encoded_bytes[16]{};
  const btsig::expected<std::size_t> encoded =
      btsig::ElectricCurrentStatistics::encode(
          value,
          btsig::span<std::uint8_t>(encoded_bytes, sizeof encoded_bytes));
  if (!encoded) {
    print_failure("encode", encoded.error());
    return false;
  }
  print_bytes("encoded", encoded_bytes, encoded.value());
  return value.average_electric_current_value == 1.5 &&
         value.standard_deviation_electric_current_value == 0.5 &&
         value.minimum_electric_current_value == 1.0 &&
         value.maximum_electric_current_value == 2.0 &&
         value.sensing_duration == 30 &&
         same_bytes(encoded_bytes, encoded.value(), wire, sizeof wire);
}

} // namespace

int main() {
  const bool ok = battery_level() && temperature() && temperature_not_known() &&
                  temperature_range() && electric_current_statistics();
  if (!ok) {
    std::printf("sample failed\n");
    return 1;
  }
  std::printf("sample ok\n");
  return 0;
}
