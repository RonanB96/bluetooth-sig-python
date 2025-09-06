#!/usr/bin/env python3
"""
Enhanced BLE Connection Debugger with Logging

This script addresses known BlueZ connection issues:
1. Race condition during service discovery (Issue #1806)
2. Service resolution timing problems
3. Connection timeout issues with certain devices

Key debugging features:
- BLEAK_LOGGING environment variable support
- Service caching strategies
- Multiple connection strategies
- Detailed timing analysis
- BlueZ D-Bus error handling

References:
- https://github.com/hbldh/bleak/issues/1806 (Race resolving services)
- https://github.com/hbldh/bleak/issues/1689 (Operation in progress)
- https://bleak.readthedocs.io/en/latest/troubleshooting.html
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


# Enable comprehensive logging
def setup_debug_logging():
    """Enable detailed Bleak and BlueZ logging."""
    # Set environment variable for Bleak logging
    os.environ["BLEAK_LOGGING"] = "1"

    # Configure Python logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s.%(msecs)03d [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Enable specific loggers
    loggers = [
        "bleak",
        "bleak.backends.bluezdbus",
        "bleak.backends.bluezdbus.client",
        "bleak.backends.bluezdbus.manager",
        "bleak.backends.bluezdbus.scanner",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

    print("🔧 Debug logging enabled (BLEAK_LOGGING=1)")


async def enhanced_device_discovery(target_address: str) -> Optional[BLEDevice]:
    """
    Enhanced device discovery with multiple strategies.

    Args:
        target_address: MAC address to find

    Returns:
        BLEDevice if found, None otherwise
    """
    print(f"🔍 Enhanced discovery for {target_address}")

    strategies = [
        ("Quick scan", {"timeout": 5.0}),
        ("Extended scan", {"timeout": 15.0}),
        ("Service-filtered scan", {"timeout": 10.0, "service_uuids": ["180A", "180F", "181A"]}),
    ]

    for strategy_name, scan_params in strategies:
        print(f"  📡 Trying {strategy_name}...")
        try:
            if "service_uuids" in scan_params:
                # Service-filtered discovery
                devices = await BleakScanner.discover(**scan_params)
                for device in devices:
                    if device.address.upper() == target_address.upper():
                        print(f"    ✅ Found via {strategy_name}")
                        return device
            else:
                # Direct address discovery
                device = await BleakScanner.find_device_by_address(
                    target_address, timeout=scan_params["timeout"]
                )
                if device:
                    print(f"    ✅ Found via {strategy_name}")
                    return device

        except Exception as e:
            print(f"    ❌ {strategy_name} failed: {e}")
            continue

    print(f"  ❌ Device {target_address} not found with any strategy")
    return None


async def connection_strategy_1_standard(device: BLEDevice) -> bool:
    """Standard connection approach."""
    print("🔌 Strategy 1: Standard connection")

    try:
        async with BleakClient(device, timeout=10.0) as client:
            print("  ✅ Connected successfully")
            print(f"  📊 Address: {client.address}")
            print(f"  📊 Connected: {client.is_connected}")

            try:
                mtu = client.mtu_size
                print(f"  📊 MTU: {mtu} bytes")
            except Exception:
                print("  📊 MTU: Unable to determine")

            services = list(client.services)
            print(f"  📊 Services: {len(services)}")

            for i, service in enumerate(services, 1):
                print(f"    {i}. {service.uuid} - {service.description}")
                chars = list(service.characteristics)
                print(f"       └─ {len(chars)} characteristics")

            return True

    except Exception as e:
        print(f"  ❌ Strategy 1 failed: {e}")
        return False


async def connection_strategy_2_cached(device: BLEDevice) -> bool:
    """Connection with service caching (dangerous_use_bleak_cache)."""
    print("🔌 Strategy 2: Cached connection")

    try:
        client = BleakClient(device, timeout=15.0)
        await client.connect(dangerous_use_bleak_cache=True)

        print("  ✅ Connected with cache enabled")
        print(f"  📊 Address: {client.address}")
        print(f"  📊 Connected: {client.is_connected}")

        try:
            services = list(client.services)
            print(f"  📊 Cached services: {len(services)}")
        except Exception as e:
            print(f"  ⚠️  Cache access failed: {e}")

        await client.disconnect()
        return True

    except Exception as e:
        print(f"  ❌ Strategy 2 failed: {e}")
        return False


async def connection_strategy_3_progressive_timeout(device: BLEDevice) -> bool:
    """Progressive timeout connection."""
    print("🔌 Strategy 3: Progressive timeout")

    timeouts = [20.0, 30.0, 45.0]

    for attempt, timeout in enumerate(timeouts, 1):
        print(f"  🔄 Attempt {attempt}/{len(timeouts)} with {timeout}s timeout")

        try:
            async with BleakClient(device, timeout=timeout) as client:
                print(f"    ✅ Connected on attempt {attempt}")

                # Quick service check
                services = list(client.services)
                print(f"    📊 Services discovered: {len(services)}")
                return True

        except asyncio.TimeoutError:
            print(f"    ⏰ Timeout after {timeout}s")
            if attempt < len(timeouts):
                print(f"    🔄 Waiting 3s before next attempt...")
                await asyncio.sleep(3)
            continue
        except Exception as e:
            print(f"    ❌ Attempt {attempt} failed: {e}")
            continue

    print("  ❌ All progressive timeout attempts failed")
    return False


async def connection_strategy_4_manual_steps(device: BLEDevice) -> bool:
    """Manual connection with step-by-step debugging."""
    print("🔌 Strategy 4: Manual step-by-step")

    try:
        print("  🔧 Creating client...")
        client = BleakClient(device, timeout=25.0)

        print("  🔧 Attempting connection...")
        start_time = time.time()
        await client.connect()
        connect_time = time.time() - start_time

        print(f"    ✅ Connected in {connect_time:.2f}s")
        print(f"    📊 Is connected: {client.is_connected}")

        if client.is_connected:
            print("  🔧 Checking MTU...")
            try:
                mtu = client.mtu_size
                print(f"    📊 MTU: {mtu} bytes")
            except Exception as e:
                print(f"    ⚠️  MTU check failed: {e}")

            print("  🔧 Discovering services...")
            services_start = time.time()
            try:
                services = list(client.services)
                services_time = time.time() - services_start
                print(f"    ✅ Services discovered in {services_time:.2f}s")
                print(f"    📊 Service count: {len(services)}")

                # Brief service analysis
                for service in services:
                    chars = list(service.characteristics)
                    print(f"      • {service.uuid}: {len(chars)} characteristics")

            except Exception as e:
                services_time = time.time() - services_start
                print(f"    ❌ Service discovery failed after {services_time:.2f}s: {e}")

            print("  🔧 Disconnecting...")
            await client.disconnect()
            print("    ✅ Disconnected cleanly")
            return True
        else:
            print("    ❌ Connection reported as failed")
            return False

    except Exception as e:
        print(f"  ❌ Strategy 4 failed: {e}")
        return False


async def debug_t52_connection(target_address: str) -> None:
    """
    Comprehensive T52 connection debugging.

    Args:
        target_address: MAC address of T52 device
    """
    print(f"🚀 T52 Enhanced Connection Debugger")
    print(f"🎯 Target: {target_address}")
    print(f"⏰ Started: {time.strftime('%H:%M:%S')}")
    print()

    # Phase 1: Device Discovery
    print("=" * 60)
    print("PHASE 1: ENHANCED DEVICE DISCOVERY")
    print("=" * 60)

    device = await enhanced_device_discovery(target_address)
    if not device:
        print("❌ Device discovery failed - cannot proceed")
        return

    print(f"✅ Device found: {device.name} ({device.address})")
    print()

    # Phase 2: Connection Strategies
    print("=" * 60)
    print("PHASE 2: CONNECTION STRATEGY TESTING")
    print("=" * 60)

    strategies = [
        connection_strategy_1_standard,
        connection_strategy_2_cached,
        connection_strategy_3_progressive_timeout,
        connection_strategy_4_manual_steps,
    ]

    successful_strategies = []

    for i, strategy in enumerate(strategies, 1):
        print(f"\n--- Strategy {i}/{len(strategies)} ---")
        try:
            success = await strategy(device)
            if success:
                successful_strategies.append(strategy.__name__)
        except Exception as e:
            print(f"❌ Strategy {i} crashed: {e}")

        # Wait between strategies to avoid interference
        if i < len(strategies):
            print("⏱️  Waiting 5s before next strategy...")
            await asyncio.sleep(5)

    # Phase 3: Results Summary
    print("\n" + "=" * 60)
    print("PHASE 3: RESULTS SUMMARY")
    print("=" * 60)

    print(f"🎯 Target device: {device.name} ({target_address})")
    print(f"✅ Successful strategies: {len(successful_strategies)}")

    if successful_strategies:
        print("🏆 Working connection methods:")
        for strategy in successful_strategies:
            print(f"  • {strategy}")
        print("\n💡 Recommendation: Use the first successful strategy for your application")
    else:
        print("❌ No strategies successful")
        print("\n🔧 Troubleshooting suggestions:")
        print("  1. Clear BlueZ cache: sudo bluetoothctl remove", target_address)
        print("  2. Restart BlueZ service: sudo systemctl restart bluetooth")
        print("  3. Check device is not paired/bonded to another system")
        print("  4. Verify device is in advertising/connectable mode")
        print("  5. Try connecting with nRF Connect app to confirm device works")

    print(f"\n⏰ Completed: {time.strftime('%H:%M:%S')}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python enhanced_ble_debugger.py <MAC_ADDRESS>")
        print("Example: python enhanced_ble_debugger.py F6:51:E1:61:32:B1")
        sys.exit(1)

    target_address = sys.argv[1]

    # Validate MAC address format
    if len(target_address) != 17 or target_address.count(":") != 5:
        print("❌ Invalid MAC address format")
        print("Expected format: AA:BB:CC:DD:EE:FF")
        sys.exit(1)

    # Setup debug logging
    setup_debug_logging()

    try:
        asyncio.run(debug_t52_connection(target_address))
    except KeyboardInterrupt:
        print("\n🛑 Debugging interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
