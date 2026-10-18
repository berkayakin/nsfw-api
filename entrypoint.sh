#!/bin/sh
# Dependencies are installed at build time; opennsfw2 and config are imported from /app
cd /app
exec python3 -m api
