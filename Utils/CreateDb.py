import pandas as pd
import sqlite3
import re

def replace_question_number(text):
    """ To convert whole question to just its question number. 
    It will be useful to detect when new table starts"""
    if isinstance(text, str):  # Check if the value is a string
        return re.sub(r'Question\s*(\d+).*', r'\1', text)
    return text  # Return the original value if it's not a string

def assign_queno_to_columns(df):
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
    df.loc[1] = df.loc[1].apply(lambda x: x.strip() if isinstance(x,str) else None) # Strip excess space from column names
    df.loc[0,0] ='Question_Number'
    df.loc[1,0] = 'Options'
    df.loc[1,1] = 'Value'
    df.loc[0,:] = df.loc[0,:].replace('','0') # To assign common columns like Total or male or female as question number 0
    return df

def clear_table(df):
    # df.rename(columns={ df.columns[1]: "Value" }, inplace = True)
    df.dropna(how='all', axis=0, inplace=True)
    df.dropna(how='all', axis=1, inplace=True)
    df.dropna(subset=['Options'],inplace=True)
    df = df.loc[:, df.columns.notna() & (df.columns != '')]
    
    # df.rename(columns={'Unnamed: 1':'Count'},inplace=True)
    
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
        # print(column)
        # print(df[column].dtype)
        # print('--------------')
            
    return df

def to_sql(df, db_name):
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
                # table_df = pd.concat([table_df,df.loc[:0]],ignore_index=True)
                # print(table_df.T)
                # print('-------------------------')
                # print(table_df.head())
                # table_df = clear_table(table_df)
                # table_df['Question_Number'] = i
                indexes = df.columns.to_list()
                print(indexes)
                table_df = table_df.drop_duplicates().T.reset_index(drop=True)
                table_df[100] = df.loc[0].tolist() 
                table_df.columns = table_df.loc[0]
                table_df = table_df.drop(index=0)
                if tables and int(x)>0:
                    table_df.drop(columns=['Total'],inplace=True) #Drop Total column
                table_df['Options'] = indexes[1:]
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
        # table_df = pd.concat([table_df,df.loc[:0]],ignore_index=True)
        table_df = table_df.T.reset_index(drop=True)
        table_df[100] = df.loc[0].tolist() 
        table_df.columns = table_df.loc[0]
        table_df = table_df.drop(index=0)
        table_df.drop(columns=['Total'],inplace=True) #Drop Total column
        table_df['Options'] = indexes[1:]
        table_df.to_sql(f'Question_{i}', conn, if_exists='replace', index=False)
        # table_df = clear_table(table_df)
        # print(table_df)
        tables.append(table_df)
    df_q = pd.read_csv('data\\Files\\Questions.csv',encoding='unicode_escape')
    df_q.to_sql('Questions', conn, if_exists='replace', index=False)
    conn.close()




def main(path, db_name):
    df = pd.read_excel(path, sheet_name='Sheet1', header=None)
    df = df.applymap(replace_question_number)
    df = assign_queno_to_columns(df)
    df.columns = df.iloc[1]
    df = df.drop(index=1).reset_index(drop=True)
    df = clear_table(df)
    to_sql(df, db_name)
    

if __name__ == "__main__":
    main('Data\\Files\\Sustain.xlsx','Sustain')
