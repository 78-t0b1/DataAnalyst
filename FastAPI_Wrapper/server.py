import sys,os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fastapi import FastAPI

from core.agent import Agent
import json
import uvicorn
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import logging
logging.basicConfig(format="{levelname}:{name}:{message}", style="{")

from Definations import SUST_DB_PATH, HOMEPAGE_PATH, STATIC_FILE_PATH

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_FILE_PATH), name="static")

class MessageRequest(BaseModel):
    message: str


agent = Agent(DB_path=SUST_DB_PATH)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    logging.info("Loading page")
    with open(HOMEPAGE_PATH) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/message")
async def root(message:str):
    return json.dumps(agent.run(message))
    
@app.post("/chat/")
async def chat(request: MessageRequest):
    # print(request)
    logging.info('Request : '+str(request))
    # Call the AI agent's method to process the message
    response = agent.run(request.message)
    logging.info('Agent Response : '+str(response))
    # print(response)
    return response

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # You can restrict this to a list of specific origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    