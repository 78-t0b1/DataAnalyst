# Survey Data Analyst


`Survey Data Analyst` is a chatbot project that utilizes **GPT-4o**, **Langchain**, **SQLite**, and **SQLAlchemy** to allow users to interact with survey dataset files through natural language. The chatbot is specifically designed to answer business questions about datasets, perform **Q&A**, and use **Retrieval-Augmented Generation (RAG)** for insights.

Excel files are converted into SQLite3 databases, and an SQL agent is used to create queries for data retrieval. The retrieved data is then processed to generate actionable business insights.

Live on : https://dataanalyst.onrender.com/




## Features:

- Interact with CSV and XLSX data through natural language.
- AI-generated insights and comparisons between datasets.
- RAG with tabular datasets.
- Visualization of insights and comparisons.



## Main underlying techniques used in this chatbot:
- **LLM chains and agents** for natural language processing and task execution.
- **FastAPI** as the web framework.
- **SQL agent** from the Langchain community for query generation.
- **SQLite3** and **SQLAlchemy** for database management.
- **Render** for deployment.

## Models used in this chatbot:
- GPT-4o: [Website](https://platform.openai.com/docs/models)

## Requirements:
- Operating System: Linux OS or Windows. (I am running this chatbot on Windows)
- OpenAI Credentials: Required for GPT functionality.
- Install SQLite3 [Link](https://www.sqlite.org/download.html).

## Folder Structure
```
DataAnalyst/
├── core/
│   ├── __init__.py
|   ├── analyst.py
│   └── agent.py
├── Data/
│   ├── DB/
│   └── Files/
├── FastAPI_Wrapper/
|   ├──static/
|   ├── __init__.py
|   ├── server.py
|   └── index2.html
├── Utils/
|   ├── CreateDb.py
|   └── DB_test.py
|
├── Definations.py
├── requirements.txt
├── .gitignore
├── .env
└── README.md
```


## Installation:
- Ensure you have Python installed along with required dependencies.
```
git clone <the repository>
cd DataAnalyst
python3 -m venv llm_venv
./bin/activate
pip install -r requirements.txt
```
## Execution:

1. Create `.env` file in which store all API keys 
```
OPENAI_API_KEY = XXXXXXXXXXXXXXXXXXXXXX
HF_API_KEY = XXXXXXXXXXXXXXXXXXXX
```

2. Activate virtual enviroment :
```cmd
cd <path_to_folder>
.\bin\activate
```

3. Run FastAPI on dev mode:
```cmd
fastapi dev FastAPI_Wrapper\server.py
```

4. Go to localhost ``127.0.0.1:8000/`` to accesss site.



## Project Schema
<div align="center">
  <img src="images/SQLagent.png" alt="Schema">
</div>

## Chatbot User Interface
<div align="center">
  <img src="images/frontpage.png" alt="ChatBot UI">
</div>

- **Get Answer**: Triggers the model to generate a response. It may take around 2-3 minutes to provide the answer.
- **Reset**: Clears the conversation history and resets the model’s memory.
- **Query**: Displays the executed SQL query that was used to generate the response.
- **Graphs**: Returns a category plot based on the data.

## Databases:
**Dataset 1 (Sustainability Research Results)** - This dataset is an Excel file containing an NxN
breakdown of the results to a survey commissioned by Bounce Insights asking consumers in the
UK various questions around how important is sustainability to consumers when they are buying
products in general & how engaged are consumers with sustainable brands or products.

**Dataset 2 (Christmas Research Results)** - This dataset is an Excel file containing an NxN
breakdown of the results to a survey commissioned by Bounce Insights asking consumers in
Ireland various questions to understand the consumers' plans for Christmas, what their plans are
overall and with spending.


## Key frameworks/libraries used in this chatbot:
- Python 3.11.3: [Documentation](https://www.python.org/downloads/release/python-3113/) 
- Langchain: [Introduction](https://python.langchain.com/docs/get_started/introduction)
- OpenAI: [Developer quickstart](https://platform.openai.com/docs/quickstart?context=python)
- SQLAlchemy [Documentation](https://www.sqlalchemy.org/)
