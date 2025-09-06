#!/bin/bash


# Scan for BLE devices and extract MAC addresses
echo "Scanning for BLE devices..."
scan_output=$(python scripts/test_real_device.py scan)

# Extract MAC addresses (format: XX:XX:XX:XX:XX:XX)
mapfile -t macs < <(echo "$scan_output" | grep -Eo '([A-F0-9]{2}:){5}[A-F0-9]{2}' | sort | uniq)

if [ ${#macs[@]} -eq 0 ]; then
    echo "No BLE devices found. Exiting."
    exit 1
fi


# Output file
output_file="ble_device_results_enhanced_$(date +"%Y%m%d_%H%M%S").txt"

# Clear the output file
true > "$output_file"


echo "Testing ${#macs[@]} BLE devices discovered by scan..."
echo "Results will be saved to: $output_file"
echo ""


# Test each discovered device
for mac in "${macs[@]}"; do
    echo "=== Running against $mac ===" | tee -a "$output_file"

    # Run the test with timeout (60 seconds per device)
    timeout 60s python scripts/test_real_device.py "$mac" 2>&1 | tee -a "$output_file"

    # Add separator
    echo "" | tee -a "$output_file"
    echo "" | tee -a "$output_file"

    # Small delay between tests
    sleep 2
done

echo "Testing completed! Results saved to: $output_file"
