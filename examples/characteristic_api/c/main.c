#include "btsig/battery_level.h"
#include "btsig/electric_current_specification.h"
#include "btsig/temperature.h"
#include "btsig/temperature_range.h"

#include <stdio.h>
#include <string.h>

static const char* status_name(btsig_status status) {
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

static void print_failure(const char* call, btsig_error error) {
    const char* field = error.field == NULL ? "-" : error.field;
    printf("  %s -> %s field=%s\n", call, status_name(error.status), field);
}

static void print_bytes(const char* label, const uint8_t* data, size_t size) {
    size_t index = 0;
    printf("  %s (%zu)", label, size);
    for (index = 0; index < size; ++index) {
        printf(" %02X", data[index]);
    }
    printf("\n");
}

static int same_bytes(const uint8_t* left, size_t left_size, const uint8_t* right, size_t right_size) {
    return left_size == right_size && memcmp(left, right, left_size) == 0;
}

static int battery_level(void) {
    const uint8_t wire[] = {0x64};
    btsig_bytes input = {wire, sizeof wire};
    btsig_battery_level value;
    btsig_error error;
    uint8_t encoded_bytes[4];
    size_t written = 0;

    printf("btsig_decode_battery_level / btsig_encode_battery_level\n");
    error = btsig_decode_battery_level(input, NULL, &value);
    if (error.status != BTSIG_OK) {
        print_failure("decode", error);
        return 0;
    }
    printf("  battery_level = %u\n", value.battery_level);

    error = btsig_encode_battery_level(&value, encoded_bytes, sizeof encoded_bytes, &written);
    if (error.status != BTSIG_OK) {
        print_failure("encode", error);
        return 0;
    }
    print_bytes("encoded", encoded_bytes, written);
    return value.battery_level == 100 && same_bytes(encoded_bytes, written, wire, sizeof wire);
}

static int temperature(void) {
    const uint8_t wire[] = {0x08, 0x07};
    btsig_bytes input = {wire, sizeof wire};
    btsig_temperature value;
    btsig_error error;
    uint8_t encoded_bytes[8];
    size_t written = 0;

    printf("btsig_decode_temperature / btsig_encode_temperature\n");
    error = btsig_decode_temperature(input, NULL, &value);
    if (error.status != BTSIG_OK) {
        print_failure("decode", error);
        return 0;
    }
    printf("  temperature = %.2f C\n", value.temperature);

    error = btsig_encode_temperature(&value, encoded_bytes, sizeof encoded_bytes, &written);
    if (error.status != BTSIG_OK) {
        print_failure("encode", error);
        return 0;
    }
    print_bytes("encoded", encoded_bytes, written);
    return value.temperature == 18.0 && same_bytes(encoded_bytes, written, wire, sizeof wire);
}

static int temperature_not_known(void) {
    const uint8_t wire[] = {0x00, 0x80};
    btsig_bytes input = {wire, sizeof wire};
    btsig_temperature value;
    btsig_error error;

    printf("btsig_decode_temperature sentinel\n");
    value.temperature = 1.0;
    error = btsig_decode_temperature(input, NULL, &value);
    print_failure("decode", error);
    return error.status == BTSIG_NOT_KNOWN && error.field != NULL && value.temperature == 1.0;
}

static int temperature_range(void) {
    const uint8_t wire[] = {0x08, 0x07, 0xF0, 0x0A};
    btsig_bytes input = {wire, sizeof wire};
    btsig_temperature_range value;
    btsig_error error;
    uint8_t encoded_bytes[8];
    size_t written = 0;

    printf("btsig_decode_temperature_range / btsig_encode_temperature_range\n");
    error = btsig_decode_temperature_range(input, NULL, &value);
    if (error.status != BTSIG_OK) {
        print_failure("decode", error);
        return 0;
    }
    printf("  minimum = %.2f C, maximum = %.2f C\n", value.minimum, value.maximum);

    error = btsig_encode_temperature_range(&value, encoded_bytes, sizeof encoded_bytes, &written);
    if (error.status != BTSIG_OK) {
        print_failure("encode", error);
        return 0;
    }
    print_bytes("encoded", encoded_bytes, written);
    return value.minimum == 18.0 && value.maximum == 28.0 && same_bytes(encoded_bytes, written, wire, sizeof wire);
}

static int electric_current_specification(void) {
    const uint8_t wire[] = {0x64, 0x00, 0x96, 0x00, 0xC8, 0x00};
    btsig_bytes input = {wire, sizeof wire};
    btsig_electric_current_specification value;
    btsig_error error;
    uint8_t encoded_bytes[16];
    size_t written = 0;

    printf("btsig_decode_electric_current_specification / "
           "btsig_encode_electric_current_specification\n");
    error = btsig_decode_electric_current_specification(input, NULL, &value);
    if (error.status != BTSIG_OK) {
        print_failure("decode", error);
        return 0;
    }
    printf("  minimum = %.2f A, typical = %.2f A, maximum = %.2f A\n", value.minimum_electric_current_value,
           value.typical_electric_current_value, value.maximum_electric_current_value);

    error = btsig_encode_electric_current_specification(&value, encoded_bytes, sizeof encoded_bytes, &written);
    if (error.status != BTSIG_OK) {
        print_failure("encode", error);
        return 0;
    }
    print_bytes("encoded", encoded_bytes, written);
    return value.minimum_electric_current_value == 1.0 && value.typical_electric_current_value == 1.5 &&
           value.maximum_electric_current_value == 2.0 && same_bytes(encoded_bytes, written, wire, sizeof wire);
}

int main(void) {
    const int ok = battery_level() && temperature() && temperature_not_known() && temperature_range() &&
                   electric_current_specification();
    if (!ok) {
        printf("sample failed\n");
        return 1;
    }
    printf("sample ok\n");
    return 0;
}
