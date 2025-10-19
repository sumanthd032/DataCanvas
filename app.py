import streamlit as st
import sqlite3
import pandas as pd
import numpy as np 
import os

st.set_page_config(
    page_title="DataCanvas: Smart SQLite Visualizer",
    layout="wide"
)

@st.cache_data 
def get_db_connection(db_path):
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

@st.cache_data
def get_tables(_conn): 
    """Fetches the list of table names from the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    try:
        tables = pd.read_sql_query(query, _conn)
        return tables['name'].tolist()
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []

@st.cache_data
def get_table_data(_conn, table_name):
    """Fetches all data from a specific table."""
    query = f'SELECT * FROM "{table_name}";'
    try:
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
        return pd.DataFrame()

st.title("DataCanvas 🎨: Smart SQLite Visualizer")

st.markdown("Welcome! Upload your SQLite database file (`.db` or `.sqlite`) to begin exploring.")

uploaded_file = st.file_uploader(
    "Choose a SQLite database file",
    type=["sqlite", "db"]
)

if uploaded_file is not None:
    temp_db_path = f"./temp_{uploaded_file.name}"
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Successfully uploaded '{uploaded_file.name}'!")

    conn = get_db_connection(temp_db_path)

    if conn:
        st.sidebar.title("Database Schema")
        table_names = get_tables(conn)
        
        if not table_names:
            st.warning("This database does not contain any tables.")
        else:
            selected_table = st.sidebar.selectbox("Select a table", table_names)
            st.sidebar.info(f"Current table: **{selected_table}**")

            df_full = get_table_data(conn, selected_table)

            if not df_full.empty:
                st.subheader(f"Preview of `{selected_table}`")
                st.dataframe(df_full.head(100))

                with st.expander("📊 Automated Data Profile", expanded=False):
                    st.markdown(f"### Profile for `{selected_table}` Table")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Number of Rows", f"{df_full.shape[0]:,}")
                    col2.metric("Number of Columns", f"{df_full.shape[1]:,}")
                    
                    st.markdown("#### Column Information & Missing Values")
                    missing_values = df_full.isnull().sum().reset_index()
                    missing_values.columns = ['Column', 'Missing Count']
                    st.dataframe(missing_values, use_container_width=True)

                    st.markdown("#### Numerical Data Statistics")
                    numeric_stats = df_full.describe().transpose()
                    st.dataframe(numeric_stats, use_container_width=True)
                
                st.divider()

                st.subheader("Run a Custom SQL Query")
                default_query = f'SELECT * FROM "{selected_table}";'
                query_text = st.text_area("SQL Query", value=default_query, height=150)
                
                if st.button("Run Query"):
                    if query_text:
                        try:
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

