#Setting Up the Environment
import os
import warnings
import dotenv
import streamlit as st
import pandas as pd
# Load Environment Variables
dotenv.load_dotenv()

# Crew AI + Tools imports
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from langchain_community.utilities.sql_database import SQLDatabase

from tools.sql_tool import (
    ExecuteSQLTool,
    GetSchemaTool,
    CheckSQLTool
)

@CrewBase
class AnalysisCrew():
    """Crew for SQL-based data analysis"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, db: SQLDatabase, tools: list = None):
        self.db = db
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.0)
        self.tools = tools or [
            ExecuteSQLTool(self.db),
            GetSchemaTool(self.db),
            CheckSQLTool(self.db, self.llm)
        ]

    # Define agents
    @agent
    def sql_dev(self) -> Agent:
        return Agent(
            config=self.agents_config["sql_dev"],
            tools=self.tools
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],
            tools=self.tools
        )


    # Define tasks
    @task
    def extract_data(self) -> Task:
        return Task(
            config=self.tasks_config["extract_data"]
        )

    @task
    def analyze_data(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_data"]
        )

    # Create the crew
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            tools=self.tools,
            process=Process.sequential,
            verbose=True,
        )
