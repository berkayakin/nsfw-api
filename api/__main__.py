from api import app
from api.functions import download_image, download_video
from config import PORT
import os
import uvicorn
import opennsfw2 as n2


@app.get("/api")
@app.get("/api/image")
async def detect_nsfw_image(url: str):
    if not url:
        return {"ERROR": "URL PARAMETER EMPTY"}
    image = await download_image(url)
    if not image:
        return {"ERROR": "IMAGE SIZE TOO LARGE OR INCORRECT URL"}
    probability = None
    try:
        probability = n2.predict_image(image)
    except Exception as e:
        print(e)
    os.remove(image)
    results = {'probability': probability}
    return results


@app.get("/api/video")
async def detect_nsfw_video(url: str):
    if not url:
        return {"ERROR": "URL PARAMETER EMPTY"}
    video = await download_video(url)
    if not video:
        return {"ERROR": "VIDEO SIZE TOO LARGE OR INCORRECT URL"}
    elapsed_seconds = None
    nsfw_probabilities = None
    try:
        elapsed_seconds, nsfw_probabilities = n2.predict_video_frames(video)
    except Exception as e:
        print(e)
    os.remove(video)
    results = {'elapsed_seconds': elapsed_seconds, 'nsfw_probabilities': nsfw_probabilities}
    return results


@app.get("/api/video_steam")
async def detect_nsfw_video_stream(url: str):
    if not url:
        return {"ERROR": "URL PARAMETER EMPTY"}
    elapsed_seconds = None
    nsfw_probabilities = None
    try:
        elapsed_seconds, nsfw_probabilities = n2.predict_video_frames(url)
    except Exception as e:
        print(e)
    results = {'elapsed_seconds': elapsed_seconds, 'nsfw_probabilities': nsfw_probabilities}
    return results


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, log_level="info")
