import os
from pyprojroot import here
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
 
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
print(load_dotenv())

from Definations import *
from core.agent import Agent

import logging
# module_logger = logging.getLogger('master_analyst')
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


class SubmitFinalAnswer(BaseModel):
    """Submit the final answer to the user based on the query results."""
    final_answer: str = Field(..., description="The questions to the SQL agent")


class MasterAnalyst:
    def __init__(self):
        sust_schema, sust_que = self.load_schema(SUST_DB_PATH)
        chris_schema, chris_que = self.load_schema(CHRIS_DB_PATH)
        self.messages = []
        self.activateSQLgen = True
        self.main_prompt = master_prompt(chris_schema, sust_schema, chris_que, sust_que)
        
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        query_gen_prompt = ChatPromptTemplate.from_messages(
            [("system", self.main_prompt), ("placeholder", "{messages}"), ("human", "{question}")]
        )
        self.query_gen = query_gen_prompt | self.llm.bind_tools(
            [SubmitFinalAnswer]
        )

        self.sust_agent = Agent(SUST_DB_PATH)
        self.chris_agent = Agent(CHRIS_DB_PATH)

        


    def load_schema(self, DB_path):
            try:
                db = SQLDatabase.from_uri(f"sqlite:///{DB_path}")
                schema = db.run("SELECT sql FROM sqlite_master WHERE type='table';")
                ques = db.run("""
                SELECT * from Questions;
            """)
                
                return schema, ques
            except Exception as e:
                logger.error("Error while runing basic queries to retrieve schema. "+e)
                raise Exception (f"Error while runing basic queries to retrieve schema. {e}")
            
    def determine_que(self):
        try:
            self.messages.append(HumanMessage(self.que))
            res = self.query_gen.invoke({"messages": self.messages, "question": self.que})
            res = res.dict()

            main_res = {'Orignal Question':self.que,'Sustain.db Question':'','Chrismas.db Question':'','Response':''}
            logger.info(f'content: {res['content']}')
            responces = res['content'].split('|')
            if len(res)==1:
                main_res['Response'] = res[0]
                self.activateSQLgen = False
            
            else:
                self.activateSQLgen = True
                for responce in responces:
                    responce = responce.strip()  
                    if responce:  
                        for key in main_res.keys():
                            if responce.startswith(key):
                                res_sep = responce.split(':', 1)  
                                main_res[res_sep[0]] = res_sep[1].strip() 

            logger.info(f"response : {responces} | SustainDB question: {main_res['Sustain.db Question']} | ChrismasDB question: {main_res['Chrismas.db Question']}") 
            return main_res
        
        except Exception as e:
            logger.error(f"Error while determining question type. {e}")
            raise Exception(f"Error while determining question type. {e}")

    def assign_agents(self, response):
        self.DB_respoce = {'Sustain.db': None, 'Chris.db': None}
        self.DB_respoce['Sustain.db'] = self.sust_agent.run(response['Sustain.db Question'])
        self.DB_respoce['Chris.db'] = self.chris_agent.run(response['Chrismas.db Question'])

        
    def final_answer_gen(self):
        self.final_analyst = PromptTemplate.from_template(FINAL_ANALYST_PROMPT)
        
        final_chain = self.final_analyst | self.llm | StrOutputParser()
        return final_chain
    
    def run(self, que):
        self.que = que
        response = self.determine_que()
        if self.activateSQLgen == False:
            return {'response': response, 'SQL': '' }
        self.assign_agents(response)
        final_chain = self.final_answer_gen()
        main_respose = final_chain.invoke({'que':self.que, 'sust':self.DB_respoce['Sustain.db']['response'], 'chris':self.DB_respoce['Chris.db']['response']})
        SQL_combine = f"""
            Sustain.db : {self.DB_respoce['Sustain.db']['SQL']}

            Chris.db : {self.DB_respoce['Chris.db']['SQL']}
"""
        sustain_image_base64 = self.DB_respoce['Sustain.db']['img']
        chris_image_base64 = self.DB_respoce['Chris.db']['img']
        self.messages.append(AIMessage(main_respose))

        return {'response': main_respose, 'SQL': SQL_combine, 'sust_table': self.DB_respoce['Sustain.db']['table'], 'chris_table': self.DB_respoce['Chris.db']['table'], 'sustain_image_base64':sustain_image_base64, 'chris_image_base64': chris_image_base64 }







