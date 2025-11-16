# Installation

## Stable release

To install Bluetooth SIG Standards Library, run this command in your terminal:

```sh
pip install bluetooth-sig
```

Or if you prefer to use `uv`:

```sh
uv add bluetooth-sig
```

## From source

The source files for Bluetooth SIG Python can be downloaded from the [Github repo](https://github.com/RonanB96/bluetooth-sig-python).

You can either clone the public repository:

```sh
git clone git://github.com/RonanB96/bluetooth-sig-python
```

Or download the [tarball](https://github.com/RonanB96/bluetooth-sig-python/tarball/main):

```sh
curl -OJL https://github.com/RonanB96/bluetooth-sig-python/tarball/main
```

Once you have a copy of the source, you can install it with:

```sh
cd bluetooth-sig-python
pip install -e .
```

### Debian/Ubuntu prerequisite packages

If you're building from source on a Debian/Ubuntu environment, several system packages
are required to build native extensions (e.g., `bluepy`) or to compile bundled
BlueZ sources. Install these before running `pip install`:

```sh
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build pkg-config libdbus-1-dev libglib2.0-dev libudev-dev libbluetooth-dev python3-dev
```

These packages ensure that `pkg-config` and the GLib/BlueZ header files are available
so Python wheels with native code compile correctly.
