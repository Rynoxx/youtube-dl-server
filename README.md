[![Docker Stars Shield](https://img.shields.io/docker/stars/rynoxx/youtube-dl-server.svg?style=flat-square)](https://hub.docker.com/r/rynoxx/youtube-dl-server/)
[![Docker Pulls Shield](https://img.shields.io/docker/pulls/rynoxx/youtube-dl-server.svg?style=flat-square)](https://hub.docker.com/r/rynoxx/youtube-dl-server/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/rynoxx/youtube-dl-server/master/LICENSE)

# youtube-dl-server

Barebones REST interface for getting youtube-dl info from a longrunning process.  
This is to improve performance over the cli implementation as we don't need to initialize the extractors again for every request.

[`starlette`](https://github.com/encode/starlette) + [`youtube-dl`](https://github.com/ytdl-org/youtube-dl).

## Running

### Docker CLI

This example uses the docker run command to create the container to run the app. Binding to port 8080

```shell
docker run -d -p 8080:8080 --name youtube-dl rynoxx/youtube-dl-server
```

### Docker Compose

This is an example service definition that could be put in `docker-compose.yml`. This service uses a VPN client container for its networking.

```yml
  youtube-dl:
    image: "rynoxx/youtube-dl-server"
    network_mode: "service:vpn"
    restart: always
```

### Python

If you have python ^3.6.0 installed in your PATH you can run it like this, providing optional environment variable overrides inline.

```shell
python3 -m uvicorn youtube_dl_server:app --port 8123
```

## Usage

Data can be fetched by supplying the `{{url}}` of the requested video through the REST interface via curl, etc.

#### Curl

```shell
curl -X GET http://{{host}}:8080/info?url={{url}}
```

#### JS Fetch

```javascript
fetch(`http://${host}:8080/info?url=${url}&format=${format}`);
```

## Implementation

The server uses [starlette](https://github.com/encode/starlette) for the web framework and [youtube-dl](https://github.com/rg3/youtube-dl) to handle the data fetching. The integration with youtube-dl makes use of their [python api](https://github.com/ytdl-org/youtube-dl#embedding-youtube-dl).

This docker image is based on [`python:3-alpine`](https://registry.hub.docker.com/_/python/) and consequently [`alpine:3`](https://hub.docker.com/_/alpine/).
