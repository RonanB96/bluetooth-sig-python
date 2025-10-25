"""Connection managers package for example adapters.

This package intentionally avoids importing adapter modules at
package import time to prevent optional back-end imports from
raising on unrelated example imports. Import specific adapters
where needed instead (e.g. ``from examples.connection_managers.bleak_retry import ...``).
"""

__all__: list[str] = []
"""Connection managers used by example code.

These modules intentionally import optional third-party backends at
module import time so that importing the connection-manager module
fails fast when the backend is absent. Tests assert this behaviour by
importing these modules under simulated missing-backend conditions.
"""

# Connection managers package.
#
# Do not import submodules here; importing submodules that depend on
# optional external libraries should be done explicitly by callers so
# tests can assert the import-time failure behaviour of each adapter
# module.
