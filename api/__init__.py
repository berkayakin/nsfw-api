from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
import hmac
import os

API_KEY = os.getenv("NSFW_API_KEY", "")
if len(API_KEY) < 32:
    raise RuntimeError("NSFW_API_KEY must be set to a random value of at least 32 characters.")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or not hmac.compare_digest(api_key.encode(), API_KEY.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


app = FastAPI(
    dependencies=[Depends(verify_api_key)],
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
api_exception = HTTPException
