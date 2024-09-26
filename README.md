# Flux HTTP Server

HTTP API for Flux image generation.

## Docker

Start the server

```bash
docker run -it \
  -p 8080:8080 \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  --gpus all \
  ghcr.io/nicolaschan/flux-http-server
```

Then generate an image

```
curl -d '{"prompt":"a sign saying hello world"}' localhost:8080/api/generate > generated.png
```
