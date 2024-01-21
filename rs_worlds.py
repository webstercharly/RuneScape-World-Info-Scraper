import requests
import struct
from enum import Enum
from io import BytesIO
from typing import Generator, Dict, Any

url = 'http://www.runescape.com/g=oldscape/slr.ws?order=LPWM'

class WorldTypes(Enum):
    MEMBERS = 1
    PVP = 4
    BOUNTY = 32
    PVP_ARENA = 64
    SKILL_TOTAL = 128
    QUEST_SPEEDRUNNING = 256
    HIGH_RISK = 1024
    LAST_MAN_STANDING = 16384
    BETA_WORLD = 65536
    NOSAVE_MODE = 33554432
    TOURNAMENT = 67108864
    FRESH_START_WORLD = 134217728
    DEADMAN = 536870912
    SEASONAL = 1073741824

def read_string(buffer: BytesIO) -> str:
    chars = []
    while (char := buffer.read(1)) != b'\x00':
        chars.append(char)
    return b''.join(chars).decode()

def parse_worlds(data: bytes) -> Generator[Dict[str, Any], None, None]:
    buffer = BytesIO(data)
    _ = buffer.read(4)  # Skip the length
    num_worlds, = struct.unpack('>H', buffer.read(2))

    for _ in range(num_worlds):
        _id, = struct.unpack('>H', buffer.read(2))
        types_mask, = struct.unpack('>I', buffer.read(4))
        address = read_string(buffer)
        activity = read_string(buffer)
        location, = struct.unpack('>B', buffer.read(1))
        players, = struct.unpack('>H', buffer.read(2))

        types = [wt.name for wt in WorldTypes if types_mask & wt.value]

        yield {
            'id': _id,
            'types': types,
            'address': address,
            'activity': activity,
            'location': location,
            'players': players
        }

def get_worlds(url: str) -> Generator[Dict[str, Any], None, None]:
    try:
        with requests.get(url) as response:
            response.raise_for_status()
            return parse_worlds(response.content)
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch data: {e}")

def main():
    try:
        for world in get_worlds(url):
            print(world)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
