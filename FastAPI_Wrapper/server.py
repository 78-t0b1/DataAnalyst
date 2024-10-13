from fastapi import FastAPI
import sys,os
from ..core.agent import Agent
import json
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from Definations import SUST_DB_PATH, HOMEPAGE_PATH

app = FastAPI()

class MessageRequest(BaseModel):
    message: str


agent = Agent(DB_path=SUST_DB_PATH)

@app.get("/", response_class=HTMLResponse)
async def read_index():
    
    with open(HOMEPAGE_PATH) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/message")
async def root(message:str):
    return json.dumps(agent.run(message))
    
@app.post("/chat/")
async def chat(request: MessageRequest):
    print(request)
    # Call the AI agent's method to process the message
    response = agent.run(request.message)
    print(response)
    return response

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # You can restrict this to a list of specific origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )

app.mount("/static", StaticFiles(directory="FastAPI_Wrapper\\static"), name="static")