from config import MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
from random import randint
import aiohttp
import aiofiles
from mimetypes import guess_extension

MAX_IMAGE_SIZE = MAX_IMAGE_SIZE * 1000000
MAX_VIDEO_SIZE = MAX_VIDEO_SIZE * 1000000


async def download(url, max_size):
    file_name = f"{randint(6969, 6999)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                if int(resp.headers['Content-Length']) > max_size:
                    return False
                content_type = resp.headers['Content-Type']
                file_extension = guess_extension(content_type)
                file_name = file_name + file_extension
                f = await aiofiles.open(file_name, mode='wb')
                await f.write(await resp.read())
                await f.close()
            else:
                return False
    return file_name


async def download_image(url):
    return await download(url, MAX_IMAGE_SIZE)


async def download_video(url):
    return await download(url, MAX_VIDEO_SIZE)
