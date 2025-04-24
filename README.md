# CS 6120 NLP Spring 2025 Final Project

## Features

- A chatbot that can imitate a person's style
- Allows user to upload their own document and ask questions related to these documents

## Tech

- Backend - Python FastAPI
- Frontend - React.js
- LLM Orchestration - LangChain
- Blob Storage - Google Cloud Storage
- Vector Storage - FAISS (Facebook AI Similarity Search)
- Deployment - Google Compute Engine
- Containerization - Docker
- 
## API Design

The main functionality of this app is provided by the following two backend api
### The imitate API
```
POST: /api/imitate

body:
{
    "text": "This is your user query",
    "character": "This is the character that you want the chatbot to imitate"
}
```

### The file upload API
In order to upload to the Cloud storage, the app needs to obtain a signed url for upload.
```
POST: /api/generate-upload-url

body:
{
    "filename": "the_name_of_your_file.pdf",
}
```



## Repository Structure
To view the code deployed and associated configuration files, please refer to the `deploy` branch.

## How to run backend 
We have provided `Dockerfile` for running the backend

To build docker image
```sh
docker build -t fastapi-backend . 
```

The requirement is that you have a signed key for uploading to Google Cloud Storage. Assume you store the key at root directory:
To start the container at port 8000:
```sh
docker run -d \                                                             
  -p 8000:8000 \
  -v $(pwd)/key.json:/app/key.json \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/key.json \
  --name fastapi-backend \
  fastapi-backend
```


####  How to run FrontEnd 
We have provided `Dockerfile` for running the frontend

To build docker image
```sh
docker build -t react-frontend .   
```

To start the frontend 
```sh
docker run -d -p 80:80 --name react-frontend react-frontend
```
You should be able to view this app on `http://localhost`
