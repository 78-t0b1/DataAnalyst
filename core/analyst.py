import os
from pyprojroot import here
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
print(load_dotenv())

from ..Definations import *
from agent import Agent





import logging
logging.basicConfig(format="{levelname}:{name}:{message}", style="{")

class SubmitFinalAnswer(BaseModel):
    """Submit the final answer to the user based on the query results."""
    final_answer: str = Field(..., description="The final answer to the user")


class MasterAnalyst:
    def __init__(self):
        sust_schema = self.load_schema(SUST_DB_PATH)
        chris_schema = self.load_schema(CHRIS_DB_PATH)

        self.main_prompt = f"""
                You are a Business Analyst who recieved this question from client. 
                You have two SQL agents one is for Chrismas.db with schema : {chris_schema} , 
                and second for Sustain.db with schema : {sust_schema}. 
                You have to decide which database above question belongs to. 
                If it belongs to both DB redifine question in two questions where one question is explicit for one and second for another.
                Please give output in following format always:
                
                Orignal Question:

                Sustain.db Question: 

                Chrismas.db Question:

                Response:

                If question belongs to only one db keep other option empty.
            """
        query_gen_prompt = ChatPromptTemplate.from_messages(
            [("system", self.main_prompt), ("placeholder", "{messages}")]
        )
        self.query_gen = query_gen_prompt | ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
            [SubmitFinalAnswer]
        )

        self.sust_agent = Agent(SUST_DB_PATH)
        self.chris_agent = Agent(CHRIS_DB_PATH)



    def load_schema(self, DB_path):
            try:
                db = SQLDatabase.from_uri(f"sqlite:///{DB_path}")
                return db.run("SELECT sql FROM sqlite_master WHERE type='table';")
            except Exception as e:
                logging.error("Error while runing basic queries to retrieve schema. "+e)
                raise "Error while runing basic queries to retrieve schema. "+e
            
    def determine_que(self, que):
        try:
            res = self.query_gen.invoke({"messages": [que]})
            res = res.dict()

            main_res = {'Orignal Question':que,'Sustain.db Question':'','Chrismas.db':'','Response':''}
            responces = res['content'].split('\n')
            if len(res)==1:
                main_res['Response'] = res[0]
            
            else:
                for responce in responces:
                    responce = responce.strip()  
                    if responce:  
                        for key in main_res.keys():
                            if responce.startswith(key):
                                res_sep = responce.split(':', 1)  
                                main_res[res_sep[0]] = res_sep[1].strip()  
            return main_res
        
        except Exception as e:
            logging.error("Error while determining question type. "+e)

    def assign_agents(self, response):
        self.DB_respoce = {'Sustain.db': None, 'Chris.db': None}
        if response['Sustain.db Question']:
            self.DB_respoce['Sustain.db'] = self.sust_agent(response['Sustain.db Question'])






