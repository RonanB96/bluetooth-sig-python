"""Test ManufacturerData and CompanyIdentifier types."""

from bluetooth_sig.types.company import CompanyIdentifier, ManufacturerData


def test_company_identifier_from_id() -> None:
    """Test CompanyIdentifier.from_id() resolution."""
    # Known company ID (Apple)
    apple = CompanyIdentifier.from_id(0x004C)
    assert apple.id == 0x004C
    assert apple.name == "Apple, Inc."

    # Unknown company ID
    unknown = CompanyIdentifier.from_id(0xFFFF)
    assert unknown.id == 0xFFFF
    assert unknown.name == "Unknown (0xFFFF)"


def test_manufacturer_data_from_bytes() -> None:
    """Test ManufacturerData.from_bytes() parsing."""
    # Apple iBeacon format: company_id (0x004C) + payload
    raw = b"\x4c\x00\x02\x15\x00\x01\x02\x03"
    mfr_data = ManufacturerData.from_bytes(raw)

    assert mfr_data.company.id == 0x004C
    assert mfr_data.company.name == "Apple, Inc."
    assert mfr_data.payload == b"\x02\x15\x00\x01\x02\x03"


def test_manufacturer_data_from_id_and_payload() -> None:
    """Test ManufacturerData.from_id_and_payload() construction."""
    payload = b"\x01\x02\x03\x04"
    mfr_data = ManufacturerData.from_id_and_payload(0x004C, payload)

    assert mfr_data.company.id == 0x004C
    assert mfr_data.company.name == "Apple, Inc."
    assert mfr_data.payload == payload


def test_manufacturer_data_immutable() -> None:
    """Test that ManufacturerData is frozen/immutable."""
    mfr_data = ManufacturerData.from_id_and_payload(0x004C, b"\x01\x02")

    try:
        mfr_data.company = CompanyIdentifier.from_id(0x0006)  # type: ignore[misc]
        raise AssertionError("Should not allow mutation")
    except AttributeError:
        pass  # Expected


def test_manufacturer_data_too_short() -> None:
    """Test ManufacturerData.from_bytes() with invalid data."""
    try:
        ManufacturerData.from_bytes(b"\x4c")  # Only 1 byte
        raise AssertionError("Should raise ValueError")
    except ValueError as e:
        assert "too short" in str(e).lower()
