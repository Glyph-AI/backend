FROM python:3.10

# install postgres client
RUN apt-get update
RUN apt-get -y install postgresql-client
RUN apt-get install poppler-utils tesseract-ocr ffmpeg libsm6 libxext6 libtesseract-dev libtesseract-dev pkg-config -y
# set workdir
WORKDIR /app

# install dependencies
COPY . .
RUN pip install -r app/requirements.txt
RUN python -c 'from sentence_transformers import SentenceTransformer; SentenceTransformer("all-mpnet-base-v2")'
# start the app
ENTRYPOINT ["/bin/sh", "./startup.sh"]