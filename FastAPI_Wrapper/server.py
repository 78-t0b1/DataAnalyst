from fastapi import FastAPI
import sys
from ..core.agent import Agent
import json
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

class MessageRequest(BaseModel):
    message: str

DB_path = 'Data\\DB\\Sustain.db'
agent = Agent(DB_path=DB_path)

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