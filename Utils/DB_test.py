from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Data\DB\Sustain.db")
print(db.dialect)
print('-------------------------')
print(db.get_usable_table_names())
print('-------------------------')

op_cols = db.run("""
    SELECT Options from "Question_1";
""")
print(op_cols)
print('-------------------------')

ques = db.run(
    """
    SELECT * from Questions;
"""
)
print(ques)
print('-------------------------')
