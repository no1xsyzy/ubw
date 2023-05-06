import asyncio
import sys

from . import gank


def main():
    asyncio.run(amain())


async def amain():
    async for dmk in gank(sys.argv[1]):
        print(dmk)
