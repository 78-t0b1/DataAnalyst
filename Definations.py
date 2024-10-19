import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root

#DB path
SUST_DB_PATH = os.path.join(ROOT_DIR, 'Data/DB/Sustain3.db')
CHRIS_DB_PATH = os.path.join(ROOT_DIR, 'Data/DB/Chrismas3.db')

#WEB
HOMEPAGE_PATH = os.path.join(ROOT_DIR, 'FastAPI_Wrapper/index2.html')
STATIC_FILE_PATH = os.path.join(ROOT_DIR, 'FastAPI_Wrapper/static')

def master_prompt(chris_schema, sust_schema, chris_que, sust_que):
    return f"""
                You are a Business Analyst who recieved this question from client. 
                You have two SQL agents one is for Chrismas database which is Chrismas.db with schema : {chris_schema} {chris_que}, 
                and second for Sustainablity database which is Sustain.db with schema : {sust_schema} {sust_que}. 
                You have to decide from which database user question can be queried. 
                If it belongs to both databases redifine question in two questions where one question is explicit for one and second for another.
                If question belongs to niether ask given question to both.
                If question belongs to only one db keep other option empty.
                Please give output in following format always:
                Orignal Question: | Sustain.db Question: | Chrismas.db Question: | Response: |
                
            """


FINAL_ANALYST_PROMPT = """
            You are a Business Analyst And you have recieved data from SQL agents. Given the following user question, and results, answer the user question and elaborate it. 
            If only one output is present just return that as an answer. Always create bullet points.                                          
            Sustain Agent output: {sust}
            Chrismas Agent output: {chris}                                              
            question: {que} 
            Answer:
            
            Try to include quantitative summaries in answer."""

