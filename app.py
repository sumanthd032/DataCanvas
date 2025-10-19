import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(
    page_title="DataCanvas: Smart SQLite Visualizer",
    layout="wide"
)

def get_db_connection(db_path):
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

def get_tables(conn):
    """Fetches the list of table names from the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    try:
        tables = pd.read_sql_query(query, conn)
        return tables['name'].tolist()
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []

st.title("DataCanvas 🎨: Smart SQLite Visualizer")

st.markdown("""
Welcome to DataCanvas! 

To get started, please upload your SQLite database file (`.db` or `.sqlite`).
""")

uploaded_file = st.file_uploader(
    "Choose a SQLite database file",
    type=["sqlite", "db"]
)

if uploaded_file is not None:
    temp_db_path = f"./temp_{uploaded_file.name}"
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Successfully uploaded and saved '{uploaded_file.name}'!")

    conn = get_db_connection(temp_db_path)

    if conn:
        st.sidebar.title("Database Schema")
        table_names = get_tables(conn)
        
        if not table_names:
            st.warning("This database does not contain any tables.")
        else:
            selected_table = st.sidebar.selectbox("Select a table to view", table_names)
            st.sidebar.info(f"You selected the table: **{selected_table}**")

            st.subheader(f"Preview of `{selected_table}`")
            preview_query = f'SELECT * FROM "{selected_table}" LIMIT 100;'
            try:
                df_preview = pd.read_sql_query(preview_query, conn)
                st.dataframe(df_preview)
            except Exception as e:
                st.error(f"An error occurred while fetching data: {e}")

            st.divider()

            st.subheader("Run a Custom SQL Query")
            default_query = f'SELECT * FROM "{selected_table}";'
            query_text = st.text_area("SQL Query", value=default_query, height=150)
            
            if st.button("Run Query"):
                if query_text:
                    try:
                        st.info("Executing your query...")
                        query_result_df = pd.read_sql_query(query_text, conn)
                        st.success("Query executed successfully!")
                        st.dataframe(query_result_df)
                    except Exception as e:
                        st.error(f"Error executing query: {e}")
                else:
                    st.warning("Please enter a query to run.")

        conn.close()
    
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

