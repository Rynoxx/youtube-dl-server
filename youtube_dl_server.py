"""
API-server to fetch data from youtube-dl.
The perk being a long-running server that doesn't need to constantly
re-initialize all extractors each time youtube-dl is to be used,
as is the case when using the CLI for youtube-dl.

If downloads are to be made,
they can easily be done using the URL in the API responses,
i.e. `response.data[0].url`
"""

import re

import os

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

# from youtube_dl import YoutubeDL
from yt_dlp import YoutubeDL

COMBINED_FORMAT_MATCH = r"\[([^\+]+=[^\+]+)\+.*\]"
COOKIEFILE = os.getenv('COOKIEFILE', '')


class ErrorLogger:
    """
    Get the warnings/error from ytdl so that we can present it through the API
    """

    def __init__(self):
        self.count = 0
        self.errors = []
        self.warnings = []

    def debug(self, msg):
        """
        Do nothing, we don't care about debug messages
        """

    def warning(self, msg):
        """
        Store warning messages for later use in self.warnings
        """
        self.warnings.append(msg)

    def error(self, msg):
        """
        Store error messages for later use in self.errors
        """
        self.errors.append(msg)


async def info(request):
    """
    The route for getting youtube-dl info from string/format
    """
    url = request.query_params["url"]
    media_format = request.query_params.get("format", "")

    # To convert standard youtube-dl format syntax to yt-dlp syntax
    # convert [x=y+a=b] to [x=y][a=b]
    if re.search(COMBINED_FORMAT_MATCH, media_format):
        in_brackets = False

        # Reverse to be able to properly replace without affecting index
        i = len(media_format)
        while i > 0:
            i -= 1
            c = media_format[i]

            # In reverse start brackets means we're now outside of brackets.
            if c == "[":
                in_brackets = False
            elif c == "]":
                in_brackets = True
            elif in_brackets and c == "+":
                media_format = media_format[:i] + "][" + media_format[i+1:]

    if len(url) == 0:
        return JSONResponse({
            "success": False,
            "errors": ["No URL specified"],
            "warnings": [],
            "data": [],
        })

    logger = ErrorLogger()

    opts = {
        "quiet": True,
        "noplaylist": True,
        "logger": logger,
        "no_color": True,
    }

    if len(media_format) != 0:
        opts["format"] = media_format

    if len(COOKIEFILE) > 0:
        opts["cookiefile"] = COOKIEFILE

    with YoutubeDL(opts) as ytdl:
        data = {}
        try:
            data = ytdl.extract_info(url, download=False)
        except Exception:
            # The logger will handle the errors.
            pass

        success = len(data) > 0

        if success:
            if 'entries' in data:
                # Remove all playlist meta-data, we only care about the content
                data = data['entries']
            else:
                data = [data]
        else:  # Ensure that we return an array on non-successful requests
            data = []

        return JSONResponse({
            "success": success,
            "errors": logger.errors,
            "warnings": logger.warnings,
            "data": data
        })


async def index(request):
    """
    Respond to / and provide some documentation to users
    """
    return JSONResponse({
        "success": True,
        "errors": [],
        "warnings": [
            "You will get no data from this route, " +
            "use /info?url={{url}}&format={{format}} instead"
        ],
        "data": []
    })

routes = [
    Route("/", endpoint=index, methods=["GET"]),
    Route("/info", endpoint=info, methods=["GET"]),
]

app = Starlette(debug=True, routes=routes)
