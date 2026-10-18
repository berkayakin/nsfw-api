from api import app, api_exception
from api.functions import download_image, download_video, remove_file, validate_url
from concurrent.futures import ThreadPoolExecutor
from config import PORT
import asyncio
import traceback
import uvicorn
import opennsfw2 as n2

# Scoring is CPU-bound and blocking. Running it on this one worker thread keeps the event
# loop free (downloads and their timeouts keep running) while still scoring one item at a
# time, so memory use stays what it was.
scoring_executor = ThreadPoolExecutor(max_workers=1)


async def score(fn, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(scoring_executor, lambda: fn(*args, **kwargs))


# Scoring failures must surface as 5xx so callers never mistake them for a "safe" result.
@app.get("/api")
@app.get("/api/image")
async def detect_nsfw_image(url: str):
    image = await download_image(url)
    try:
        probability = await score(n2.predict_image, image)
    except Exception:
        traceback.print_exc()
        raise api_exception(status_code=500, detail="Image scoring failed.")
    finally:
        remove_file(image)
    return {'probability': probability}


@app.get("/api/video")
async def detect_nsfw_video(url: str):
    video = await download_video(url)
    try:
        elapsed_seconds, nsfw_probabilities = await score(n2.predict_video_frames, video, progress_bar=False)
    except Exception:
        traceback.print_exc()
        raise api_exception(status_code=500, detail="Video scoring failed.")
    finally:
        remove_file(video)
    # An unreadable video yields no frames; that's a failure, not a clean result
    if not nsfw_probabilities:
        raise api_exception(status_code=500, detail="Video scoring returned no frames.")
    return {'elapsed_seconds': elapsed_seconds, 'probabilities': nsfw_probabilities}


@app.get("/api/video_stream")
async def detect_nsfw_video_stream(url: str):
    validate_url(url)
    try:
        elapsed_seconds, nsfw_probabilities = await score(n2.predict_video_frames, url, progress_bar=False)
    except Exception:
        traceback.print_exc()
        raise api_exception(status_code=500, detail="Video scoring failed.")
    if not nsfw_probabilities:
        raise api_exception(status_code=500, detail="Video scoring returned no frames.")
    return {'elapsed_seconds': elapsed_seconds, 'nsfw_probabilities': nsfw_probabilities}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, log_level="info")
