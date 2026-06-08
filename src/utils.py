import mysql.connector
import pandas as pd


# ---------------- DB CONNECTION ---------------- #
def get_connection():  
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sql@1234",
        database="logistics_dataset"
    )

   
def fetch_data(query, params=None):
    try:
       
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        df = pd.DataFrame(rows, columns=columns)

        cursor.close()
        conn.close()
        return df
    finally:
        if conn:
            conn.close()




    



