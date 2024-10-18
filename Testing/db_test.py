from sqlalchemy import create_engine
from sqlalchemy import text
# Set up your SQL database connection directly using SQLAlchemy
engine = create_engine('sqlite:///Data/DB/Sustain.db')

# Execute your query using the SQLAlchemy engine
query = """SELECT OPTIONS,
       "Yes "
FROM Question_15
ORDER BY "Yes " DESC
LIMIT 10;"""

# Get column names from the query
with engine.connect() as connection:
    result_proxy = connection.execute(text(query))
    
    # Get column names from the result proxy
    column_names = result_proxy.keys()

print(column_names)

print(result_proxy.all())
