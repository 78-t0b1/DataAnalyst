from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine, text
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
from langchain_community.utilities import SQLDatabase
import sqlparse
import os,sys
import pandas as pd
import base64
import matplotlib.pyplot as plt
import io

import logging
logging.basicConfig(format="{levelname}:{name}:{message}", style="{")


current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

class Agent:
    def __init__(self, DB_path) -> None:
        self.load_DB(DB_path)
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0 )
        self.sql_agent = create_sql_agent(self.llm, db=self.db, agent_type="openai-tools", verbose=True,agent_executor_kwargs = {"return_intermediate_steps": True})
        self.query_gen_system = PromptTemplate.from_template("""
            You are a Business Analyst And you have recieved data from SQL agents. Given the following user question and results, answer the user question and elaborate it. 
            question: {input}
            result: {output} 
            Answer:""")
        
        self.chain = self.query_gen_system | self.llm | StrOutputParser()
        logging.info('Agent is created!')
        

    def load_DB(self, DB_path):
        try:
            self.engine = create_engine(f"sqlite:///{DB_path}")
            self.db = SQLDatabase(self.engine)
            # self.db = SQLDatabase.from_uri(f"sqlite:///{DB_path}")
            # self.op_cols = self.db.run("""
            #     SELECT Options from "Question_1";
            # """)
            # self.ques = self.db.run(
            #     """
            #     SELECT * from Questions;
            # """
            # )
            op_cols_query = """
                 SELECT Options from "Question_1";
             """
            ques_query = """
                 SELECT * from Questions;
             """
            with self.engine.connect() as connection:
                self.op_cols = connection.execute(text(op_cols_query)).all()
                self.ques = connection.execute(text(ques_query)).all()
            

        except Exception as e:
            logging.error(f"Error while runing basic queries to retrieve questions ans options. {e}")
            raise f"Error while runing basic queries to retrieve questions ans options. {e}"
        
    def run(self, question):
        try:
            logging.info('Agent is running!')
            if question:
                self.response = self.sql_agent.invoke({
                        "input": f" Option column has values : {self.op_cols} And Questions table contain {self.ques} from survey which are linked with all other tables. Keeping that in mind {question}. If you use LIMIT in query use LIMIT 1"
                    })
                query = self.get_exec_query()
                query = self.format_sql(query)
                
                response = self.chain.invoke(self.response)

                table = self.get_query_op_json(query)

                return {'response':response,'SQL':query, 'table': table, 'img': self.img_base64}
            else:
                response = 'No question asked'
                return {'response':response,'SQL':'', 'table': '', 'img': ''}
        
        except Exception as e:
            raise f"Error while runing SQL agent. {e}"
        
    
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

    def get_query_op_json(self, query):
        try:
            with self.engine.connect() as connection:
                self.df = pd.read_sql(query, connection)
                self.generate_graphs()
                return self.df.to_json()
            
        except:
            return None
        
    def generate_graphs(self):
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            self.df.plot(kind='bar', ax=ax)
            buf = io.BytesIO()
            # plt.show(fig)
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)

            # Encode the image in base64
            self.img_base64 = 'data:image/png;base64,' +base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            self.img_base64 = e
        


