# Flux HTTP Server

HTTP API for Flux image generation.

## Docker

```bash
docker run -it \
  -p 8080:8080 \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  --gpus all \
  ghcr.io/nicolaschan/flux-http-server
```

