import pandas as pd
import sqlite3
import re

def replace_question_number(text):
    """ To convert whole question to just its question number. 
    It will be useful to detect when new table starts"""
    if isinstance(text, str):  
        return re.sub(r'Question\s*(\d+).*', r'\1', text)
    return text  

def assign_queno_to_columns(df):
    """
    In excel question number is mentioned only for first column of options I assigned it to all columns

    Args:
    df : Excel data which is converted to dataframe.
    """
    s = ''
    i = 0
    for x in df.loc[0]:
        if isinstance(x, str):
            if x.isnumeric():
                s = x.strip()
        try:
            df.loc[0,i] = s
        except:
            pass
        i+=1
    df.loc[1] = df.loc[1].apply(lambda x: x.strip() if isinstance(x,str) else None)
    df.loc[0,0] ='Question_Number'
    df.loc[1,0] = 'Options'
    df.loc[1,1] = 'Value'
    df.loc[0,:] = df.loc[0,:].replace('','0') 
    return df

def clear_table(df):
    """
    To perform Data cleaning on given excel.

    Args:
    df : Excel data which is converted to dataframe.
    
    """
    df.dropna(how='all', axis=0, inplace=True)
    df.dropna(how='all', axis=1, inplace=True)
    df.dropna(subset=['Options'],inplace=True)
    df = df.loc[:, df.columns.notna() & (df.columns != '')]
    df.reset_index(inplace=True)
    df.drop(columns=['index'],inplace=True)
    # df['Options'] = df['Options'].apply(str)
    df['Options'] = df['Options'].apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))
    df['Options'] = df['Options'].astype("string")
    print(df['Options'].dtype)

    for column in df.columns:
        if isinstance(df[column], pd.DataFrame):
            print(f"Column '{column}' contains DataFrame(s):")
            print(df[column])
        try:
            if df[column].dtype == 'object':  # Check if the column type is 'object' (potentially unsupported types)
                df[column] = df[column].astype('double')  # Convert the column to string
        except:
            print(column)
    return df

def to_sql(df, db_name):
    """
    Convert dataframe to database. create multiple tables using question number and questions as delimiters.

    Args: 
    df: Excel data which is converted to dataframe.
    db_name: Name of database
    """
    tables = []
    current_table = []
    conn = sqlite3.connect(f'{db_name}.db')
    i = 0 ##Question number
    # Iterate over the rows of the dataframe starting after the header row (row 0)

    q_no = df.loc[0].tolist()

    for idx, row in df.iterrows():
        x = str(row[0])
        if idx == 0:
            continue  # Skip the header row since we already got column names
        
        if x.isdigit() and len(x) < 3:  # If the row contains a question (adjust condition as needed)
            # If a current table exists, append it to the list of tables
            if current_table:
                # Convert collected rows into a DataFrame and assign column names
                
                table_df = pd.DataFrame(current_table, columns=df.columns)
                indexes = df.columns.str.replace('\n', '').str.strip()
                indexes = indexes.to_list()
                table_df = table_df.drop_duplicates().T.reset_index(drop=True)
                table_df[100] = df.loc[0].tolist() 
                table_df.columns = table_df.loc[0]
                table_df.columns = table_df.columns.str.replace('\n', '').str.strip()
                table_df = table_df.drop(index=0)
                table_df['Question_Number'] = i
                if tables and int(x)>0:
                    table_df.drop(columns=['Total'],inplace=True) #Drop Total column
                table_df['Options'] = indexes[1:]
                table_df = clear_table(table_df)
                tables.append(table_df)

                print(table_df)
                print('-------------------------')

                table_df.to_sql(f'Question_{i}', conn, if_exists='replace', index=False)
                current_table = []  # Reset for the next table
                i+=1
                print(x)
        else:
            current_table.append(row.tolist())  # Collect rows into the current table

    # Append the last table if any rows were collected
    if current_table:
        table_df = pd.DataFrame(current_table, columns=df.columns)
        table_df = table_df.T.reset_index(drop=True)
        table_df[100] = df.loc[0].tolist() 
        table_df.columns = table_df.loc[0]
        table_df = table_df.drop(index=0)
        table_df.drop(columns=['Total'],inplace=True) #Drop Total column
        table_df['Options'] = indexes[1:]
        table_df.to_sql(f'Question_{i}', conn, if_exists='replace', index=False)
        tables.append(table_df)
    df_q = pd.read_csv('data\\Files\\Questions_chrismas.csv',encoding='unicode_escape') # change questions<>.csv according to dataset processed.
    df_q.to_sql('Questions', conn, if_exists='replace', index=False)
    conn.close()

def main(path, db_name):
    """
    Main flow

    Args: 
    df: Excel data which is converted to dataframe.
    db_name: Name of database
    """
    df = pd.read_excel(path, sheet_name='Sheet1', header=None)
    df = df.applymap(replace_question_number)
    df = assign_queno_to_columns(df)
    df.columns = df.iloc[1]
    df = df.drop(index=1).reset_index(drop=True)
    df = clear_table(df)
    to_sql(df, db_name)
    

if __name__ == "__main__":
    main('Data\\Files\\Chrismas.xlsx','Chrismas3')
