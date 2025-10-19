import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns 

# --- Page Configuration ---
st.set_page_config(
    page_title="DataCanvas: Smart SQLite Visualizer",
    layout="wide"
)

# --- Helper Functions ---
@st.cache_resource
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

# --- Application Title ---
st.title("DataCanvas 🎨: Smart SQLite Visualizer")
st.markdown("Welcome! Upload your SQLite database file (`.db` or `.sqlite`) to begin exploring.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a SQLite database file",
    type=["sqlite", "db"]
)

# --- Main Logic ---
if uploaded_file is not None:
    temp_dir = "temp_data"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_db_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Successfully uploaded and processing '{uploaded_file.name}'!")

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
                # --- 1. Display Table Preview ---
                st.subheader(f"Preview of `{selected_table}`")
                st.dataframe(df_full.head(100))

                # --- 2. Automated Data Profiling ---
                with st.expander("📊 Automated Data Profile", expanded=False):
                    st.markdown(f"### Profile for `{selected_table}` Table")
                    col1, col2 = st.columns(2)
                    col1.metric("Number of Rows", f"{df_full.shape[0]:,}")
                    col2.metric("Number of Columns", f"{df_full.shape[1]:,}")
                    
                    st.markdown("#### Column Information & Missing Values")
                    missing_values = df_full.isnull().sum().reset_index()
                    missing_values.columns = ['Column', 'Missing Count']
                    st.dataframe(missing_values, width='stretch')

                    st.markdown("#### Numerical Data Statistics")
                    numeric_stats = df_full.describe().transpose()
                    st.dataframe(numeric_stats, width='stretch')

                # --- 3. Smart Visualizations ---
                st.subheader("💡 Smart Visualizations")
                
                # Univariate Analysis
                with st.expander("Analyze a Single Column's Distribution", expanded=True):
                    all_columns = df_full.columns.tolist()
                    column_to_visualize = st.selectbox(
                        "Select a column to visualize", 
                        all_columns, 
                        index=None, 
                        placeholder="Choose a column..."
                    )

                    if column_to_visualize:
                        column_data = df_full[column_to_visualize]

                        if pd.api.types.is_numeric_dtype(column_data):
                            st.markdown(f"**Distribution of `{column_to_visualize}` (Histogram)**")
                            fig, ax = plt.subplots()
                            ax.hist(column_data.dropna(), bins='auto', edgecolor='black')
                            ax.set_xlabel(column_to_visualize)
                            ax.set_ylabel("Frequency")
                            st.pyplot(fig)
                            plt.close(fig)

                        elif pd.api.types.is_object_dtype(column_data) or column_data.nunique() < 25:
                            st.markdown(f"**Value Counts for `{column_to_visualize}` (Bar Chart)**")
                            value_counts = column_data.value_counts().nlargest(25)
                            st.bar_chart(value_counts)
                        
                        else:
                            st.info(f"Column `{column_to_visualize}` is categorical but has too many unique values for a bar chart ( > 25).")

                # --- 4. Correlation Analysis (NEW) ---
                with st.expander("Analyze Relationships Between Columns (Bivariate Analysis)", expanded=True):
                    st.markdown("#### Correlation Heatmap")
                    st.markdown("A heatmap shows how strongly numerical columns are related to each other. Values close to 1 (dark red) mean a strong positive correlation, and values close to -1 (dark blue) mean a strong negative correlation.")

                    numeric_cols = df_full.select_dtypes(include=np.number).columns.tolist()
                    
                    if len(numeric_cols) < 2:
                        st.info("Not enough numerical columns (at least 2 required) to generate a correlation heatmap.")
                    else:
                        corr_matrix = df_full[numeric_cols].corr()
                        
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                        ax.tick_params(axis='x', rotation=45)
                        st.pyplot(fig)
                        plt.close(fig)

                st.divider()

                # --- 5. Custom SQL Query Runner ---
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

