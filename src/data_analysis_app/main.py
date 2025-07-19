import os
import streamlit as st
import pandas as pd
import sqlite3
import re

from crews.analysis_crew.analysis_crew import AnalysisCrew
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

from tools.sql_tool import (
    ExecuteSQLTool,
    CheckSQLTool,
    GetSchemaTool
)

# -------- Upload CSV and save into SQLite --------
def handle_uploaded_file(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.to_csv("temp.csv", index=False)
    conn = sqlite3.connect("temp_db.sqlite")
    df.to_sql("data_table", conn, if_exists="replace", index=False)

    count = conn.execute("SELECT COUNT(*) FROM data_table").fetchone()[0]

    conn.close()

    st.write(f"✅ Successfully wrote {count} rows to the SQLite database.")
    
    return df

# -------- Extract code block from agent output (if any) --------
def extract_code_block(raw_text: str) -> str:
    match = re.search(r"```python(.*?)```", raw_text, re.DOTALL)
    return match.group(1).strip() if match else ""

# -------- Streamlit UI settings --------
st.set_page_config(page_title="CrewAI App", layout="wide")
st.title("💻 CrewAI Multi-Agent App")

uploaded_file = st.file_uploader("📁 Upload a CSV file", type="csv")
if not uploaded_file:
    st.info("Please upload a CSV to continue.")
    st.stop()

df = handle_uploaded_file(uploaded_file)

# -------- Initialize SQL database and tools --------
try:
    db = SQLDatabase.from_uri("sqlite:///temp_db.sqlite")
except ValueError as e:
    st.error(f"❌ Error loading database: {e}")
    st.stop()

# ✅ Initialize LLM for SQL checking
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# ✅ Get table schema using custom tool
schema_tool = GetSchemaTool()
schema_info = schema_tool._run()

tools = [
    ExecuteSQLTool(db=db),
    CheckSQLTool(db=db, llm=llm),
    GetSchemaTool()
]

# -------- Display schema and sample data --------
st.success("✅ Data uploaded and loaded into database.")
st.expander("📄 Structured schema from tool").code(schema_info)
st.dataframe(df.head())

# -------- Data analysis section --------
st.subheader("Ask a question about the data")
query = st.text_input("e.g. What is the average price per product category?")

if st.button("Run Analysis"):
    if not query:
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Running analysis..."):
        result = AnalysisCrew(db=db, tools=tools).crew().kickoff(
            inputs={
                "question": query,
                "schema": schema_info
            }
        )

    st.success("✅ Analysis complete!")

    for output in result.tasks_output:
        st.subheader("Agent Says:")
        st.markdown(output.raw or "No output")
        if "SELECT" in (output.raw or "").upper():
            st.code(output.raw, language="sql")
