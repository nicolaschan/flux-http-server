from aiohttp import web
from diffusers import DiffusionPipeline, FluxPipeline
from huggingface_hub import snapshot_download
from io import BytesIO
from transformers import T5EncoderModel
import gc
import torch

def pipeline():
    snapshot = snapshot_download(repo_id="black-forest-labs/FLUX.1-schnell")
    pipeline = FluxPipeline.from_pretrained(snapshot, torch_dtype=torch.bfloat16) #, text_encoder_2=None, text_encoder=None)
    pipeline.enable_sequential_cpu_offload()
    # pipeline.enable_model_cpu_offload()
    return pipeline

async def hello(request):
    return web.Response(text="flux-api")

def query_param(request, param, default=None):
    value = request.query.get(param)
    return default if value is None else value

async def generate(request):
    seed = int(query_param(request, 'seed', 0))
    prompt = query_param(request, 'prompt', 'text saying "no prompt"')
    steps = int(query_param(request, 'steps', 4))
    max_sequence_length = int(query_param(request, 'max_sequence_length', 256))

    generator = torch.Generator("cuda").manual_seed(seed)
    args = {
      # "prompt_embeds": prompt_embeds.bfloat16(),
      # "pooled_prompt_embeds": pooled_prompt_embeds.bfloat16(),
      "prompt": [prompt],
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
    pipe = request.app['pipe']
    output = pipe(**args, **kwargs)
    image = output.images[0]
    png_output = BytesIO()
    image.save(png_output, format='PNG')
    png_data = png_output.getvalue()
    return web.Response(body=png_data, content_type='image/png')

async def main():
    app = web.Application()
    pipe = pipeline()
    app['pipe'] = pipe
    app.add_routes([
        web.get('/', hello),
        web.get('/api/generate', generate)
    ])
    return app

if __name__ == '__main__':
    print(f'Flux Pipeline with {torch.cuda.is_available()=}')
    web.run_app(main())
