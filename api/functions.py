from config import MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
from random import randint
import aiohttp
import aiofiles

MAX_IMAGE_SIZE = MAX_IMAGE_SIZE * 1000000
MAX_VIDEO_SIZE = MAX_VIDEO_SIZE * 1000000


async def download(url, file_name, max_size):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                if int(resp.headers['Content-Length']) > max_size:
                    return False
                f = await aiofiles.open(file_name, mode='wb')
                await f.write(await resp.read())
                await f.close()
            else:
                return False
    return file_name

async def download_image(url):
    file_name = f"{randint(6969, 6999)}"
    return await download(url, file_name, MAX_IMAGE_SIZE)


async def download_video(url):
    file_name = f"{randint(6969, 6999)}"
    return await download(url, file_name, MAX_VIDEO_SIZE)
