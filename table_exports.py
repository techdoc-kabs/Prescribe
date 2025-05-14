import streamlit as st
import mysql.connector

# def export_table():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="kabs_db" 
#         )
#         cursor = conn.cursor()
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS mhpss_db.student_users 
#             LIKE kabs_db.student_users
#         """)
#         cursor.execute("""
#             INSERT INTO mhpss_db.student_users 
#             SELECT * FROM kabs_db.student_users
#         """)

#         conn.commit()
#         st.success("Table exported successfully from kabs_db to mhpss_db!")

#     except mysql.connector.Error as e:
#         st.error(f"Error: {e}")

#     finally:
#         cursor.close()
#         conn.close()

# if st.button("Export Table"):
#     export_table()



import mysql.connector
import streamlit as st

def export_tables(tables):
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="kabs_db"  # Source database
        )
        cursor = conn.cursor()

        for table in tables:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS mhpss_db.{table} 
                LIKE kabs_db.{table}
            """)

            # Copy data
            cursor.execute(f"""
                INSERT INTO mhpss_db.{table} 
                SELECT * FROM kabs_db.{table}
            """)

        conn.commit()
        st.success(f"Tables {', '.join(tables)} exported successfully!")

    except mysql.connector.Error as e:
        st.error(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

tables_to_export = ['diagnoses']  # Add more as needed

if st.button("Export Tables"):
    export_tables(tables_to_export)
