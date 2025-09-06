from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import time

try:
    import simplepyble as simpleble
except Exception as e:
    print('Import simplepyble failed:', e)
    raise

print('SimplePyBLE version loaded')
adapters = simpleble.Adapter.get_adapters()
print('Adapters:', adapters)
if not adapters:
    print('No adapters')
    sys.exit(1)
adapter = adapters[0]
print('Using adapter:', adapter.identifier())

# quick scan
adapter.scan_start()
time.sleep(3)
adapter.scan_stop()
results = adapter.scan_get_results()
print(f'Found {len(results)} devices')

target = None
for p in results:
    try:
        if hasattr(p, 'address') and p.address() == 'F6:51:E1:61:32:B1':
            target = p
            break
        if p.identifier() == 'F6:51:E1:61:32:B1':
            target = p
            break
    except Exception:
        continue

if not target:
    print('Target not found')
    sys.exit(2)

print('Target peripheral found:', target.identifier(), getattr(target, 'address', lambda: 'N/A')())
print('Connecting...')
target.connect()
print('Connected:', target.is_connected())

services = target.services()
print('Services:', len(services))
if not services:
    print('No services')
    target.disconnect()
    sys.exit(0)

svc = services[0]
chars = svc.characteristics()
print('First service has', len(chars), 'characteristics')
if not chars:
    target.disconnect()
    sys.exit(0)

char = chars[0]
print('Characteristic object:', type(char))
print('\nATTRIBUTES AND METHODS:')
for name in sorted(dir(char)):
    print(name)

# try to find readable attributes
candidates = [n for n in dir(char) if 'read' in n.lower() or 'value' in n.lower() or 'get' in n.lower()]
print('\nPotential read-like methods:', candidates)

# safe disconnect
target.disconnect()
print('Disconnected')
