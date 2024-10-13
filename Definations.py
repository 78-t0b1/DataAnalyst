import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root

#DB path
SUST_DB_PATH = os.path.join(ROOT_DIR, 'Data\\DB\\Sustain.db')
CHRIS_DB_PATH = os.path.join(ROOT_DIR, 'Data\\DB\\Chrismas.db')

#WEB
HOMEPAGE_PATH = os.path.join(ROOT_DIR, 'FastAPI_Wrapper\\index2.html')
