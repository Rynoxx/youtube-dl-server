"""
API-server to fetch data from youtube-dl.
The perk being a long-running server that doesn't need to constantly re-initialize all extractors
each time youtube-dl is to be used, as is the case when using the CLI for youtube-dl.

If downloads are to be made,
they can easily be done using the URL in the API responses, i.e. `response.data[0].url`
"""

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from youtube_dl import YoutubeDL
from youtube_dl.utils import GeoRestrictedError, ExtractorError, MaxDownloadsReached

YTDL_DEFAULT_FORMAT = "bestvideo/bestaudio" #"bestaudio[ext=webm+acodec=opus+asr=48000]/bestaudio"

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
    media_format = request.query_params.get("format", YTDL_DEFAULT_FORMAT)

    logger = ErrorLogger()

    opts = {
        "quiet": True,
        "noplaylist": True,
        "format": media_format,
        "logger": logger,
    }

    with YoutubeDL(opts) as ytdl:
        data = {}
        try:
            data = ytdl.extract_info(url, download=False)
        except GeoRestrictedError as e:
            logger.errors.append(e.msg)
        except ExtractorError as e:  # An error we somewhat expected
            logger.errors.append(e)
        except MaxDownloadsReached as e:
            logger.errors.append(e)
        except Exception as e:
            logger.errors.append(e)

        success = len(data) > 0

        if success:
            if 'entries' in data:
                # Remove all playlist meta-data, we only care about the content.
                data = data['entries']
            else:
                data = [data]

        return JSONResponse(
            {
                "success": success,
                "errors": logger.errors,
                "warnings": logger.warnings,
                "data": data
            }
        )

async def index(request):
    """
    Index route to ensure that we respond to / and provide some documentation to users
    """
    return JSONResponse(
        {
            "success": True,
            "errors": [],
            "warnings": ["You will get no data from this route, use /info?url={{url}}&format={{format}} instead"],
            "data": []
        }
    )

routes = [
    Route("/", endpoint=index, methods=["GET"]),
    Route("/info", endpoint=info, methods=["GET"]),
]

app = Starlette(debug=True, routes=routes)
