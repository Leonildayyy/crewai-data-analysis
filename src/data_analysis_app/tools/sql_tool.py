from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLCheckerTool

# ----- Input Schemas ----- #
class SQLQueryInput(BaseModel):
    sql_query: str = Field(..., description="The SQL query to run on the database.")

class NoInput(BaseModel):
    pass

# ----- Custom Tool Classes ----- #
class ExecuteSQLTool(BaseTool):
    args_schema: Type[BaseModel] = SQLQueryInput

    def __init__(self, db: SQLDatabase):
        super().__init__(
            name="execute_sql",
            description="Executes a SQL query and returns the result."
        )
        object.__setattr__(self, 'db', db)

    def _run(self, sql_query: str) -> str:
        try:
            return self.db.run(sql_query)
        except Exception as e:
            return f"[SQL Execution Error] {e} | Query: {sql_query}"

class CheckSQLTool(BaseTool):
    args_schema: Type[BaseModel] = SQLQueryInput

    def __init__(self, db: SQLDatabase, llm):
        super().__init__(
            name="check_sql",
            description="Checks if a SQL query is syntactically correct."
        )
        object.__setattr__(self, 'tool', QuerySQLCheckerTool(db=db, llm=llm))
        object.__setattr__(self, 'db', db)

    def _run(self, sql_query: str) -> str:
        try:
            return self.tool.invoke({"query": sql_query})
        except Exception as e:
            return f"[SQL Check Error] {str(e)}"

class GetSchemaTool(BaseTool):
    args_schema: Type[BaseModel] = NoInput

    def __init__(self, db_path: str = "temp_db.sqlite", table_name: str = "data_table"):
        super().__init__(
            name="get_structured_schema",
            description="Returns a structured column list (with types) for the given table in SQLite."
        )
        object.__setattr__(self, 'db_path', db_path)
        object.__setattr__(self, 'table_name', table_name)

    def _run(self) -> str:
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name});")
            columns = cursor.fetchall()
            conn.close()

            column_info = "\n".join([f"- {col[1]} ({col[2]})" for col in columns])
            return f"Table: {self.table_name}\nColumns:\n{column_info}"
        except Exception as e:
            return f"[Schema Build Error] {str(e)}"
