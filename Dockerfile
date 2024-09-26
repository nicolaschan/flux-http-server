FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT [ "python", "main.py" ]
