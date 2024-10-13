from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
from langchain_community.utilities import SQLDatabase
import sqlparse
import os,sys

import logging
logging.basicConfig(format="{levelname}:{name}:{message}", style="{")


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

class Agent:
    def __init__(self, DB_path) -> None:
        self.load_DB(DB_path)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.sql_agent = create_sql_agent(self.llm, db=self.db, agent_type="openai-tools", verbose=True,agent_executor_kwargs = {"return_intermediate_steps": True})
        self.query_gen_system = PromptTemplate.from_template("""
            You are a Business Analyst And you have recieved data from SQL agent. Given the following user question, and result, answer the user question. 
            question: {input}
            result: {output} 
            Answer:""")
        
        self.chain = self.query_gen_system | self.llm | StrOutputParser()
        logging.info('Agent is created!')
        

    def load_DB(self, DB_path):
        try:
            self.db = SQLDatabase.from_uri(f"sqlite:///{DB_path}")
            self.op_cols = self.db.run("""
                SELECT Options from "Question_1";
            """)
            self.ques = self.db.run(
                """
                SELECT * from Questions;
            """
            )
        except Exception as e:
            logging.error("Error while runing basic queries to retrieve questions ans options. "+e)
            raise "Error while runing basic queries to retrieve questions ans options. "+e
        
    def run(self, question):
        logging.info('Agent is running!')
        self.response = self.sql_agent.invoke({
                "input": f" Option column has values : {self.op_cols} And Questions table contain {self.ques} from survey which are linked with all other tables. Keeping that in mind {question}"
            })
        
        query = self.get_exec_query()
        query = self.format_sql(query)
        
        response = self.chain.invoke(self.response)

        return {'response':response,'SQL':query}
    
    def get_exec_query(self):
        try:
            queries = []
            for (log, output) in self.response["intermediate_steps"]:
                if log.tool == 'sql_db_query':
                    queries.append(log.tool_input)
            return queries[-1]['query']
        except Exception as e:
            logging.error(f"Probllem while returning query. {e}"+ str(self.response))
            return f"Probllem while returning query. {e}"+ str(self.response)
        
    def format_sql(self, query:str):
        formatted_query = sqlparse.format(query, reindent=True, keyword_case='upper')
        return formatted_query



