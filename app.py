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
    layout="wide",
    initial_sidebar_state="expanded",
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

# --- Main Application ---
st.title("DataCanvas 🎨: Smart SQLite Visualizer")

# --- Sidebar ---
with st.sidebar:
    st.header("Upload & Explore")
    uploaded_file = st.file_uploader(
        "Choose a SQLite database file",
        type=["sqlite", "db"]
    )
    st.info("Upload your SQLite database to automatically generate insights and visualizations.")
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")


# --- Main Logic ---
if uploaded_file is None:
    st.info("👋 Welcome to DataCanvas! Please upload a database file from the sidebar to get started.")
    st.image("https://placehold.co/800x300/F0F2F6/4F8BF9?text=Upload+a+Database+to+Begin&font=inter", use_container_width=True)

else:
    # Save uploaded file to a temporary location
    temp_dir = "temp_data"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_db_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ Successfully uploaded and processing '{uploaded_file.name}'!")

    conn = get_db_connection(temp_db_path)

    if conn:
        with st.sidebar:
            st.subheader("Database Schema")
            table_names = get_tables(conn)
            
            if not table_names:
                st.warning("This database does not contain any tables.")
            else:
                selected_table = st.selectbox("Select a table", table_names)
                st.info(f"Current table: **{selected_table}**")

        if 'selected_table' in locals() and selected_table:
            df_full = get_table_data(conn, selected_table)

            if not df_full.empty:
                st.subheader(f"Preview of `{selected_table}`")
                st.dataframe(df_full.head(100))

                # --- Tabbed Interface for Analysis ---
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Profile", "💡 Single Column Analysis", "🔗 Bivariate Analysis", "🧠 Automated Insights"])

                # --- Tab 1: Automated Data Profiling ---
                with tab1:
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

                # --- Tab 2: Univariate Analysis ---
                with tab2:
                    st.markdown("### Analyze a Single Column's Distribution")
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
                            ax.set_title(f"Distribution of {column_to_visualize}")
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

                # --- Tab 3: Bivariate Analysis ---
                with tab3:
                    st.markdown("### Analyze Relationships Between Columns")
                    
                    st.markdown("#### Correlation Heatmap (Numerical vs. Numerical)")
                    numeric_cols = df_full.select_dtypes(include=np.number).columns.tolist()
                    
                    if len(numeric_cols) < 2:
                        st.info("Not enough numerical columns (at least 2 required) to generate a correlation heatmap.")
                    else:
                        corr_matrix = df_full[numeric_cols].corr()
                        fig, ax = plt.subplots(figsize=(10, 8))
                        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                        ax.set_title(f"Correlation Matrix for `{selected_table}`")
                        ax.tick_params(axis='x', rotation=45)
                        st.pyplot(fig)
                        plt.close(fig)

                    st.divider()

                    st.markdown("#### Distribution Analysis (Numerical vs. Categorical)")
                    categorical_cols = df_full.select_dtypes(include=['object', 'category']).columns.tolist()
                    
                    if len(numeric_cols) < 1 or len(categorical_cols) < 1:
                        st.info("Box plot requires at least one numerical and one categorical column.")
                    else:
                        col1, col2 = st.columns(2)
                        with col1:
                            cat_col = st.selectbox("Select a categorical column", categorical_cols, index=None, placeholder="Choose a category...")
                        with col2:
                            num_col = st.selectbox("Select a numerical column", numeric_cols, index=None, placeholder="Choose a value...")

                        if cat_col and num_col:
                            fig, ax = plt.subplots()
                            sns.boxplot(data=df_full, x=cat_col, y=num_col, ax=ax)
                            ax.set_title(f"Distribution of {num_col} by {cat_col}")
                            ax.tick_params(axis='x', rotation=45)
                            st.pyplot(fig)
                            plt.close(fig)
                
                # --- Tab 4: Automated Insights ---
                with tab4:
                    st.markdown("### Key Insights & Observations")
                    
                    # 1. High Correlation Insight
                    st.subheader("📈 Correlation Insights")
                    if 'corr_matrix' in locals() and not corr_matrix.empty:
                        # Unstack the matrix to easily find max correlation
                        corr_pairs = corr_matrix.unstack()
                        # Sort pairs
                        sorted_pairs = corr_pairs.sort_values(kind="quicksort", ascending=False)
                        # Remove self-correlations (where value is 1.0)
                        non_self_corr = sorted_pairs[sorted_pairs != 1.0]
                        
                        if not non_self_corr.empty:
                            highest_corr_pair = non_self_corr.head(1)
                            col1, col2 = highest_corr_pair.index[0]
                            corr_value = highest_corr_pair.values[0]
                            
                            if abs(corr_value) > 0.7:
                                st.success(f"**Strong Correlation Found:** `{col1}` and `{col2}` have a strong correlation of **{corr_value:.2f}**. This suggests a significant relationship worth exploring further.")
                            elif abs(corr_value) > 0.5:
                                st.info(f"**Moderate Correlation Found:** `{col1}` and `{col2}` have a moderate correlation of **{corr_value:.2f}**.")
                        else:
                            st.info("No significant correlations found between numerical columns.")
                    else:
                        st.info("Correlation analysis requires at least two numerical columns.")

                    # 2. Missing Values Insight
                    st.subheader("🗑️ Missing Data Insights")
                    total_rows = len(df_full)
                    missing_summary = df_full.isnull().sum()
                    missing_summary = missing_summary[missing_summary > 0] # Filter columns with missing data
                    
                    if not missing_summary.empty:
                        most_missing_col = missing_summary.idxmax()
                        missing_count = missing_summary.max()
                        missing_percentage = (missing_count / total_rows) * 100
                        
                        if missing_percentage > 30:
                            st.warning(f"**High Missing Data:** The column `{most_missing_col}` has **{missing_percentage:.1f}%** missing values ({missing_count} rows). This could impact analysis and model accuracy.")
                        else:
                            st.info(f"The column with the most missing values is `{most_missing_col}` with **{missing_percentage:.1f}%** missing data.")
                    else:
                        st.success("🎉 **Great News!** No missing values were found in this table.")

                    # 3. High Cardinality Insight
                    st.subheader("🇇 Cardinality Insights")
                    if 'categorical_cols' in locals() and categorical_cols:
                        high_cardinality_cols = []
                        for col in categorical_cols:
                            unique_count = df_full[col].nunique()
                            if unique_count > 50: # Threshold for "high" cardinality
                                high_cardinality_cols.append(f"`{col}` ({unique_count} unique values)")
                        
                        if high_cardinality_cols:
                            st.warning(f"**High Cardinality Detected:** The following categorical columns have many unique values, which might make them difficult to use for grouping: {', '.join(high_cardinality_cols)}.")
                        else:
                            st.info("No categorical columns with unusually high numbers of unique values were detected.")
                    else:
                        st.info("No categorical columns available to analyze for cardinality.")


                st.divider()

                # --- Custom SQL Query Runner ---
                with st.expander("🚀 Run a Custom SQL Query"):
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

