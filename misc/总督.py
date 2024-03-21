import asyncio
import json

import aiohttp

STREAMER_MID = 1521415


async def fetch_live(live_id, session):
    async with session.get('https://ukamnads.icu/api/v2/live', params={'liveId': live_id}) as resp:
        print(f'{live_id=} {resp.status=}')
        text_ = await resp.text()
        print(f'{live_id=} {text_=}')
        return json.loads(text_)


async def main():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        async with session.get('https://ukamnads.icu/api/v2/channel', params={'uId': STREAMER_MID}) as resp:
            live_ids = map(lambda x: x['liveId'],
                           filter(lambda x: x['totalIncome'] >= 19998,
                                  (await resp.json())['data']['lives']))

        for live_id in live_ids:
            await asyncio.sleep(1)
            async with session.get('https://ukamnads.icu/api/v2/live', params={'liveId': live_id}) as resp:
                json_ = await resp.json()
                for danmaku in json_['data']['data']['danmakus']:
                    if danmaku['type'] == 2 and danmaku['message'] == "总督":
                        print(danmaku)


if __name__ == '__main__':
    asyncio.run(main())
