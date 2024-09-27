from aiohttp import web
from diffusers import DiffusionPipeline, FluxPipeline
from huggingface_hub import snapshot_download
from io import BytesIO
from transformers import T5EncoderModel
import asyncio
import base64
import json
import gc
import torch

def pipeline():
    snapshot = snapshot_download(repo_id="black-forest-labs/FLUX.1-schnell")
    pipeline = FluxPipeline.from_pretrained(snapshot, torch_dtype=torch.bfloat16)
    pipeline.enable_sequential_cpu_offload()
    return pipeline

async def hello(request):
    return web.Response(text="flux-api")

def query_param(request, param, default=None):
    value = request.query.get(param)
    return default if value is None else value

def body_param(body, param, default=None):
    return body.get(param, default)

def generate_blocking(pipe, prompt, seed = 0, steps = 4, max_sequence_length = 256, count = 4):
    generator = torch.Generator("cuda").manual_seed(seed)
    args = {
      "prompt": [prompt] * count,
      "guidance_scale": 0.0,
      "generator": generator,
      "num_inference_steps": steps,
      "max_sequence_length": max_sequence_length,
      "output_type": "pil"
    }
    kwargs = {
        "width": 1024,
        "height": 1024 
    }
    output = pipe(**args, **kwargs)
    return output.images

async def generate(*args, **kwargs):
    return await asyncio.to_thread(generate_blocking, *args, **kwargs)

def base64_image(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    png_data = buffer.getvalue()
    base64_encoded = base64.b64encode(png_data).decode("utf-8")
    data_url = f"data:image/png;base64,{base64_encoded}"
    return data_url

async def batch_api(request):
    body = await request.json()

    seed = int(query_param(request, 'seed', 0))
    prompt = body_param(body, 'prompt', 'text saying "no prompt"')
    steps = int(query_param(request, 'steps', 4))
    max_sequence_length = int(query_param(request, 'max_sequence_length', 256))
    count = int(query_param(request, 'count', 4))
    pipe = request.app['pipe']

    images = await generate(pipe, prompt, seed=seed, steps=steps, max_sequence_length=max_sequence_length, count=count)
    base64_images = [ base64_image(image) for image in images ]
    base64_images_json = json.dumps({ "images": base64_images })
    return web.Response(text=base64_images_json, content_type='application/json')

async def main():
    app = web.Application()
    pipe = pipeline()
    app['pipe'] = pipe
    app.add_routes([
        web.get('/', hello),
        web.post('/api/batch', batch_api)
    ])
    return app

if __name__ == '__main__':
    print(f'Flux Pipeline with {torch.cuda.is_available()=}')
    web.run_app(main())
