import pyodbc

def test_connection():
    conn_str = 'DSN=oracledb;UID=rajasri;PWD=Rajasri'

    try:
        conn = pyodbc.connect(conn_str)
        print("Connection successful!")
        cursor = conn.cursor()
        cursor.execute("SELECT *FROM users WHERE username = 'ram'")
        for row in cursor:
            print(row)
        conn.close()
    except Exception as e:
        print("Connection failed: ", e)


test_connection()
