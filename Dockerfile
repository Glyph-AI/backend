FROM python:3.10

# install postgres client
RUN apt-get update
RUN apt-get -y install postgresql-client
RUN apt-get install poppler-utils tesseract-ocr ffmpeg libsm6 libxext6 libtesseract-dev libtesseract-dev pkg-config -y

# Bring in embedding model
RUN pip install sentence-transformers
RUN python -c 'from sentence_transformers import SentenceTransformer; model = SentenceTransformer("all-mpnet-base-v2"); model.save("/embedding_model")'

# set workdir
WORKDIR /app

# install dependencies
COPY ./app/requirements.txt ./app/requirements.txt
RUN pip install -r app/requirements.txt

# copy source code
COPY . .
# start the app
ENTRYPOINT ["/bin/sh", "./startup.sh"]