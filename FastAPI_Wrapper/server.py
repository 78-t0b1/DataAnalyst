import sys,os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from fastapi import FastAPI

from core.analyst import MasterAnalyst
import uvicorn
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from Definations import HOMEPAGE_PATH, STATIC_FILE_PATH

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO) 

file_handler = logging.FileHandler('app.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_FILE_PATH), name="static")

class MessageRequest(BaseModel):
    message: str

master = MasterAnalyst()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    To load main page
    """
    logging.info("Loading page")
    with open(HOMEPAGE_PATH) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/reset/")
async def reset():
    """
    To reset context memory 
    """
    # Reset or clear the chat context here
    master.messages = []
    logger.info(f"Message chain : {master.messages}")
    return {"message": "Chat context reset successfully."}
    
@app.post("/chat/")
async def chat(request: MessageRequest):
    """
    Call the AI agent's method to process the message
    """
    logger.info(f"Request : {request}")
    response = master.run(request.message)
    logger.info(f"Message chain : {master.messages}")
    return response




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    