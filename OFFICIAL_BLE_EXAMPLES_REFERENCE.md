# Official BLE Library Examples Reference

## Overview

This document contains the exact official examples from major BLE libraries to use as templates for creating enhanced examples that showcase the Bluetooth SIG translation library integration.

## Bleak Library Examples

### 1. Service Explorer (`service_explorer.py`)

**Purpose**: Discover and enumerate all services, characteristics, and descriptors on a device
**Key Features**: Service discovery, characteristic reading, descriptor access, error handling

```python
"""
Service Explorer
----------------

An example showing how to access and print out the services, characteristics and
descriptors of a connected GATT server.

Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
"""

import argparse
import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)

class Args(argparse.Namespace):
    name: Optional[str]
    address: Optional[str]
    macos_use_bdaddr: bool
    services: list[str]
    pair: bool
    debug: bool

async def main(args: Args):
    logger.info("starting scan...")

    if args.address:
        device = await BleakScanner.find_device_by_address(
            args.address, cb={"use_bdaddr": args.macos_use_bdaddr}
        )
        if device is None:
            logger.error("could not find device with address '%s'", args.address)
            return
    elif args.name:
        device = await BleakScanner.find_device_by_name(
            args.name, cb={"use_bdaddr": args.macos_use_bdaddr}
        )
        if device is None:
            logger.error("could not find device with name '%s'", args.name)
            return
    else:
        raise ValueError("Either --name or --address must be provided")

    logger.info("connecting to device...")

    async with BleakClient(
        device,
        pair=args.pair,
        services=args.services,
        timeout=90 if args.pair else 10,
    ) as client:
        logger.info("connected to %s (%s)", client.name, client.address)

        for service in client.services:
            logger.info("[Service] %s", service)

            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char)
                        extra = f", Value: {value}"
                    except Exception as e:
                        extra = f", Error: {e}"
                else:
                    extra = ""

                if "write-without-response" in char.properties:
                    extra += f", Max write w/o rsp size: {char.max_write_without_response_size}"

                logger.info(
                    "  [Characteristic] %s (%s)%s",
                    char,
                    ",".join(char.properties),
                    extra,
                )

                for descriptor in char.descriptors:
                    try:
                        value = await client.read_gatt_descriptor(descriptor)
                        logger.info("    [Descriptor] %s, Value: %r", descriptor, value)
                    except Exception as e:
                        logger.error("    [Descriptor] %s, Error: %s", descriptor, e)

        logger.info("disconnecting...")

    logger.info("disconnected")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    device_group = parser.add_mutually_exclusive_group(required=True)

    device_group.add_argument(
        "--name",
        metavar="<name>",
        help="the name of the bluetooth device to connect to",
    )
    device_group.add_argument(
        "--address",
        metavar="<address>",
        help="the address of the bluetooth device to connect to",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "--services",
        nargs="+",
        metavar="<uuid>",
        help="if provided, only enumerate matching service(s)",
    )

    parser.add_argument(
        "--pair",
        action="store_true",
        help="pair with the device before connecting if not already paired",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the log level to debug",
    )

    args = parser.parse_args(namespace=Args())

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(args))
```

### 2. Enable Notifications (`enable_notifications.py`)

**Purpose**: Enable notifications on a characteristic and handle incoming data
**Key Features**: Notification setup, callback handling, device scanning

```python
"""
Notifications
-------------

Example showing how to add notifications to a characteristic and handle the responses.

Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>
"""

import argparse
import asyncio
import logging
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

logger = logging.getLogger(__name__)

class Args(argparse.Namespace):
    name: Optional[str]
    address: Optional[str]
    macos_use_bdaddr: bool
    characteristic: str
    debug: bool

def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    logger.info("%s: %r", characteristic.description, data)

async def main(args: Args):
    logger.info("starting scan...")

    if args.address:
        device = await BleakScanner.find_device_by_address(
            args.address, cb={"use_bdaddr": args.macos_use_bdaddr}
        )
        if device is None:
            logger.error("could not find device with address '%s'", args.address)
            return
    elif args.name:
        device = await BleakScanner.find_device_by_name(
            args.name, cb={"use_bdaddr": args.macos_use_bdaddr}
        )
        if device is None:
            logger.error("could not find device with name '%s'", args.name)
            return
    else:
        raise ValueError("Either --name or --address must be provided")

    logger.info("connecting to device...")

    async with BleakClient(device) as client:
        logger.info("Connected")

        await client.start_notify(args.characteristic, notification_handler)
        await asyncio.sleep(5.0)
        await client.stop_notify(args.characteristic)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    device_group = parser.add_mutually_exclusive_group(required=True)

    device_group.add_argument(
        "--name",
        metavar="<name>",
        help="the name of the bluetooth device to connect to",
    )
    device_group.add_argument(
        "--address",
        metavar="<address>",
        help="the address of the bluetooth device to connect to",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "characteristic",
        metavar="<notify uuid>",
        help="UUID of a characteristic that supports notifications",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the log level to debug",
    )

    args = parser.parse_args(namespace=Args())

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(args))
```

### 3. Device Discovery (`discover.py`)

**Purpose**: Scan for and discover BLE devices with optional service filtering
**Key Features**: Device scanning, service UUID filtering, advertisement data

```python
"""
Scan/Discovery
--------------

Example showing how to scan for BLE devices.

Updated on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
"""

import argparse
import asyncio

from bleak import BleakScanner

class Args(argparse.Namespace):
    macos_use_bdaddr: bool
    services: list[str]

async def main(args: Args):
    print("scanning for 5 seconds, please wait...")

    devices = await BleakScanner.discover(
        return_adv=True,
        service_uuids=args.services,
        cb={"use_bdaddr": args.macos_use_bdaddr},
    )

    for d, a in devices.values():
        print()
        print(d)
        print("-" * len(str(d)))
        print(a)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--services",
        metavar="<uuid>",
        nargs="*",
        help="UUIDs of one or more services to filter for",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    args = parser.parse_args(namespace=Args())

    asyncio.run(main(args))
```

### 4. TI SensorTag Example (`sensortag.py`)

**Purpose**: Complete real-world device interaction with TI CC2650 SensorTag
**Key Features**: Device-specific implementation, multiple characteristic reads, notifications, I/O control

```python
"""
TI CC2650 SensorTag
-------------------

An example connecting to a TI CC2650 SensorTag.

Created on 2018-01-10 by hbldh <henrik.blidh@nedomkull.com>
"""
import asyncio
import platform
import sys

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.uuids import normalize_uuid_16, uuid16_dict

ADDRESS = (
    "24:71:89:cc:09:05"
    if platform.system() != "Darwin"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)

uuid16_lookup = {v: normalize_uuid_16(k) for k, v in uuid16_dict.items()}

SYSTEM_ID_UUID = uuid16_lookup["System ID"]
MODEL_NBR_UUID = uuid16_lookup["Model Number String"]
DEVICE_NAME_UUID = uuid16_lookup["Device Name"]
FIRMWARE_REV_UUID = uuid16_lookup["Firmware Revision String"]
HARDWARE_REV_UUID = uuid16_lookup["Hardware Revision String"]
SOFTWARE_REV_UUID = uuid16_lookup["Software Revision String"]
MANUFACTURER_NAME_UUID = uuid16_lookup["Manufacturer Name String"]
BATTERY_LEVEL_UUID = uuid16_lookup["Battery Level"]
KEY_PRESS_UUID = normalize_uuid_16(0xFFE1)

# I/O test points on SensorTag.
IO_DATA_CHAR_UUID = "f000aa65-0451-4000-b000-000000000000"
IO_CONFIG_CHAR_UUID = "f000aa66-0451-4000-b000-000000000000"

async def main(address: str):
    async with BleakClient(address, winrt={"use_cached_services": True}) as client:
        print(f"Connected: {client.is_connected}")

        system_id = await client.read_gatt_char(SYSTEM_ID_UUID)
        print(
            "System ID: {0}".format(
                ":".join(["{:02x}".format(x) for x in system_id[::-1]])
            )
        )

        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

        try:
            device_name = await client.read_gatt_char(DEVICE_NAME_UUID)
            print("Device Name: {0}".format("".join(map(chr, device_name))))
        except Exception:
            pass

        manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
        print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

        firmware_revision = await client.read_gatt_char(FIRMWARE_REV_UUID)
        print("Firmware Revision: {0}".format("".join(map(chr, firmware_revision))))

        hardware_revision = await client.read_gatt_char(HARDWARE_REV_UUID)
        print("Hardware Revision: {0}".format("".join(map(chr, hardware_revision))))

        software_revision = await client.read_gatt_char(SOFTWARE_REV_UUID)
        print("Software Revision: {0}".format("".join(map(chr, software_revision))))

        battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
        print("Battery Level: {0}%".format(int(battery_level[0])))

        async def notification_handler(
            characteristic: BleakGATTCharacteristic, data: bytearray
        ):
            print(f"{characteristic.description}: {data}")

        # Turn on the red light on the Sensor Tag by writing to I/O Data and I/O Config.
        write_value = bytearray([0x01])
        value = await client.read_gatt_char(IO_DATA_CHAR_UUID)
        print("I/O Data Pre-Write Value: {0}".format(value))

        await client.write_gatt_char(IO_DATA_CHAR_UUID, write_value, response=True)

        value = await client.read_gatt_char(IO_DATA_CHAR_UUID)
        print("I/O Data Post-Write Value: {0}".format(value))
        assert value == write_value

        write_value = bytearray([0x01])
        value = await client.read_gatt_char(IO_CONFIG_CHAR_UUID)
        print("I/O Config Pre-Write Value: {0}".format(value))

        await client.write_gatt_char(IO_CONFIG_CHAR_UUID, write_value, response=True)

        value = await client.read_gatt_char(IO_CONFIG_CHAR_UUID)
        print("I/O Config Post-Write Value: {0}".format(value))
        assert value == write_value

        # Try notifications with key presses.
        await client.start_notify(KEY_PRESS_UUID, notification_handler)
        await asyncio.sleep(5.0)
        await client.stop_notify(KEY_PRESS_UUID)

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))
```

### 5. UART Service Example (`uart_service.py`)

**Purpose**: Demonstrate Nordic UART service for bidirectional communication
**Key Features**: Service filtering, bidirectional communication, data streaming

```python
"""
UART Service
-------------

An example showing how to write a simple program using the Nordic Semiconductor
(nRF) UART service.
"""

import asyncio
import sys
from itertools import count, takewhile
from typing import Iterator

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

def sliced(data: bytes, n: int) -> Iterator[bytes]:
    """
    Slice *data* into chunks of size *n*. The last chunk will be smaller if
    len(data) is not divisible by *n*.
    """
    return takewhile(len, (data[i:i + n] for i in count(0, n)))

async def uart_terminal():
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):
        # This assumes that the device includes the UART service UUID in the
        # advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if UART_SERVICE_UUID.lower() in adv.service_uuids:
            return True
        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)

    if device is None:
        print("no matching device found, you may need to edit match_nus_uuid().")
        sys.exit(1)

    def handle_disconnect(_: BleakClient):
        print("Device was disconnected, goodbye.")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: BleakGATTCharacteristic, data: bytearray):
        print("received:", data)

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        print("Connected, start typing and press ENTER...")

        loop = asyncio.get_running_loop()
        nus = client.services.get_service(UART_SERVICE_UUID)
        assert nus is not None, "UART service not found"
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
        assert rx_char is not None, "UART RX characteristic not found"

        while True:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break

            # Writing without response requires that the data can fit in a
            # single BLE packet. We can use the max_write_without_response_size
            # property to split the data into chunks that will fit.
            for s in sliced(data, rx_char.max_write_without_response_size):
                await client.write_gatt_char(rx_char, s, response=False)

            print("sent:", data)

if __name__ == "__main__":
    try:
        asyncio.run(uart_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
```

### 6. Two Devices Simultaneous Connection (`two_devices.py`)

**Purpose**: Connect to and manage multiple BLE devices simultaneously
**Key Features**: Concurrent connections, locking, notification handling from multiple devices

```python
import argparse
import asyncio
import contextlib
import logging
from typing import Iterable

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

class Args(argparse.Namespace):
    device1: str
    uuid1: str
    device2: str
    uuid2: str
    by_address: bool
    macos_use_bdaddr: bool
    debug: bool

async def connect_to_device(
    lock: asyncio.Lock,
    by_address: bool,
    macos_use_bdaddr: bool,
    name_or_address: str,
    notify_uuid: str,
):
    """
    Scan and connect to a device then print notifications for 10 seconds before
    disconnecting.
    """
    logging.info("starting %s task", name_or_address)

    try:
        async with contextlib.AsyncExitStack() as stack:
            # Trying to establish a connection to two devices at the same time
            # can cause errors, so use a lock to avoid this.
            async with lock:
                logging.info("scanning for %s", name_or_address)

                if by_address:
                    device = await BleakScanner.find_device_by_address(
                        name_or_address, cb={"use_bdaddr": macos_use_bdaddr}
                    )
                else:
                    device = await BleakScanner.find_device_by_name(name_or_address)

                logging.info("stopped scanning for %s", name_or_address)

                if device is None:
                    logging.error("%s not found", name_or_address)
                    return

                logging.info("connecting to %s", name_or_address)

                client = await stack.enter_async_context(BleakClient(device))

                logging.info("connected to %s", name_or_address)

                stack.callback(logging.info, "disconnecting from %s", name_or_address)

            # The lock is released here. The device is still connected and the
            # Bluetooth adapter is now free to scan and connect another device
            # without disconnecting this one.

            def callback(_: BleakGATTCharacteristic, data: bytearray) -> None:
                logging.info("%s received %r", name_or_address, data)

            await client.start_notify(notify_uuid, callback)
            await asyncio.sleep(10.0)
            await client.stop_notify(notify_uuid)

        # The stack context manager exits here, triggering disconnection.

        logging.info("disconnected from %s", name_or_address)

    except Exception:
        logging.exception("error with %s", name_or_address)

async def main(
    by_address: bool,
    macos_use_bdaddr: bool,
    addresses: Iterable[str],
    uuids: Iterable[str],
):
    lock = asyncio.Lock()

    await asyncio.gather(
        *(
            connect_to_device(lock, by_address, macos_use_bdaddr, address, uuid)
            for address, uuid in zip(addresses, uuids)
        )
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "device1",
        metavar="<device>",
        help="Bluetooth name or address of first device connect to",
    )
    parser.add_argument(
        "uuid1",
        metavar="<uuid>",
        help="notification characteristic UUID on first device",
    )
    parser.add_argument(
        "device2",
        metavar="<device>",
        help="Bluetooth name or address of second device to connect to",
    )
    parser.add_argument(
        "uuid2",
        metavar="<uuid>",
        help="notification characteristic UUID on second device",
    )

    parser.add_argument(
        "--by-address",
        action="store_true",
        help="when true treat <device> args as Bluetooth address instead of name",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the log level to debug",
    )

    args = parser.parse_args(namespace=Args())

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(
        main(
            args.by_address,
            args.macos_use_bdaddr,
            (args.device1, args.device2),
            (args.uuid1, args.uuid2),
        )
    )
```

## SimplePyBLE Integration Patterns

Based on the existing example in your project, here are the key SimplePyBLE patterns:

### Basic SimplePyBLE Scanner Pattern

```python
import simplepyble

def scan_and_connect():
    """Basic SimplePyBLE scanning and connection pattern."""
    # Get the first available adapter
    adapter = simplepyble.Adapter.get_adapters()[0]

    # Scan for devices
    adapter.scan_for(5000)  # 5 seconds

    # Get scan results
    peripherals = adapter.scan_get_results()

    if peripherals:
        peripheral = peripherals[0]

        # Connect to device
        peripheral.connect()

        # Enumerate services and characteristics
        for service in peripheral.services():
            print(f"Service: {service.uuid()}")

            for characteristic in service.characteristics():
                print(f"  Characteristic: {characteristic.uuid()}")

                # Read characteristic if readable
                if characteristic.can_read():
                    try:
                        data = peripheral.read(service.uuid(), characteristic.uuid())
                        print(f"    Data: {data.hex()}")
                    except Exception as e:
                        print(f"    Read error: {e}")

        # Disconnect
        peripheral.disconnect()
```

## Integration Template Patterns

### 1. Service Discovery with SIG Parsing

**Template**: Enhanced service explorer that uses SIG library for parsing
**Based on**: `service_explorer.py` + SIG translation

### 2. Device-Specific Examples

**Template**: Real device interactions with comprehensive parsing
**Based on**: `sensortag.py` + SIG translation

### 3. Notification Handling with SIG Parsing

**Template**: Notification setup with automatic parsing
**Based on**: `enable_notifications.py` + SIG translation

### 4. Multi-Device Management

**Template**: Concurrent device handling with SIG parsing
**Based on**: `two_devices.py` + SIG translation

### 5. UART/Communication Services

**Template**: Bidirectional communication with data parsing
**Based on**: `uart_service.py` + SIG translation

## Common Patterns Across Libraries

### Device Discovery Pattern
```python
# Bleak
devices = await BleakScanner.discover()
device = await BleakScanner.find_device_by_address(address)

# SimplePyBLE
adapter = simplepyble.Adapter.get_adapters()[0]
adapter.scan_for(5000)
peripherals = adapter.scan_get_results()
```

### Connection Pattern
```python
# Bleak
async with BleakClient(device) as client:
    # operations

# SimplePyBLE
peripheral.connect()
try:
    # operations
finally:
    peripheral.disconnect()
```

### Characteristic Reading Pattern
```python
# Bleak
data = await client.read_gatt_char(char_uuid)

# SimplePyBLE
data = peripheral.read(service_uuid, char_uuid)
```

### Notification Pattern
```python
# Bleak
def notification_handler(char, data):
    # handle data
await client.start_notify(char_uuid, notification_handler)

# SimplePyBLE
def notification_callback(data):
    # handle data
peripheral.notify(service_uuid, char_uuid, notification_callback)
```

## Implementation Strategy

1. **Take each official example pattern**
2. **Add Bluetooth SIG library integration at the parsing points**
3. **Maintain the exact same connection/communication logic**
4. **Demonstrate the enhanced parsing capabilities**
5. **Show side-by-side comparisons where appropriate**

This reference provides the exact foundation for creating enhanced examples that showcase your Bluetooth SIG library's parsing capabilities within proven, official BLE library patterns.
