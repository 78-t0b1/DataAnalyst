from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
from langchain_community.utilities import SQLDatabase

class Agent:
    def __init__(self, DB_path) -> None:
        self.load_DB(DB_path)
        self.sql_agent = create_sql_agent(self.llm, db=self.db, agent_type="openai-tools", verbose=True)
        self.query_gen_system = PromptTemplate.from_template("""
            You are a Business Analyst And you have recieved data from SQL agent. Given the following user question, and result, answer the user question. 
            question: {input}
            result: {output} 
            Answer:""")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.chain = self.sql_agent | self.query_gen_system | self.llm | StrOutputParser()
        

    def load_DB(self, DB_path):
        self.db = SQLDatabase.from_uri(f"sqlite:///{DB_path}")
        self.op_cols = self.db.run("""
            SELECT Options from "Question_1";
        """)
        self.ques = self.db.run(
            """
            SELECT * from Questions;
        """
        )
        
    def run(self, question):
        response = self.chain.invoke(
            {
                "input": f" Option column has values : {self.op_cols} And Questions table contain {self.ques} from survey which are linked with all other tables. Keeping that in mind {question}"
            }
        )
        return response

