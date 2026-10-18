from config import MAX_IMAGE_SIZE, MAX_VIDEO_SIZE
from fastapi import HTTPException
from mimetypes import guess_extension
from urllib.parse import urlparse
import aiofiles
import aiohttp
import os
import tempfile
import uuid

MAX_IMAGE_SIZE = MAX_IMAGE_SIZE * 1000000
MAX_VIDEO_SIZE = MAX_VIDEO_SIZE * 1000000
DOWNLOAD_TIMEOUT = aiohttp.ClientTimeout(total=60, connect=5)
CHUNK_SIZE = 64 * 1024


def validate_url(url):
    if not url:
        raise HTTPException(status_code=400, detail="Parameter url is empty.")
    if urlparse(url).scheme not in ("http", "https"):
        raise HTTPException(status_code=422, detail="Only http(s) URLs are allowed.")


async def download(url, max_size):
    """
    Download url into a uniquely named file in the temp dir and return its path.
    Raises HTTPException when the file can't be downloaded or is too large.
    """
    validate_url(url)

    file_path = None
    try:
        async with aiohttp.ClientSession(timeout=DOWNLOAD_TIMEOUT) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=502, detail=f"Media download failed with HTTP {resp.status}.")
                if resp.content_length is not None and resp.content_length > max_size:
                    raise HTTPException(status_code=413, detail="Media is too large.")

                content_type = resp.headers.get('Content-Type', '').split(';')[0].strip()
                file_extension = guess_extension(content_type) or ''
                file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}{file_extension}")

                # Don't trust Content-Length: enforce the limit on the bytes actually received
                size = 0
                async with aiofiles.open(file_path, mode='wb') as f:
                    async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                        size += len(chunk)
                        if size > max_size:
                            raise HTTPException(status_code=413, detail="Media is too large.")
                        await f.write(chunk)
    except Exception as e:
        remove_file(file_path)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=502, detail=f"Media download failed: {e}")

    return file_path


def remove_file(file_path):
    if file_path and os.path.exists(file_path):
        os.remove(file_path)


async def download_image(url):
    return await download(url, MAX_IMAGE_SIZE)


async def download_video(url):
    return await download(url, MAX_VIDEO_SIZE)
