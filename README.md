### CrewAI Data Analysis App

A simple Streamlit app using CrewAI and OpenAI to analyze uploaded CSV files. Users can inspect the data schema and ask questions to get instant insights.

### Features

- Upload and analyze CSV files
- Use natural language to explore your data
- Modular setup using CrewAI agents and tools

### Getting Started

1. Initialize the CrewAI project structure
Run the following command to generate the modular structure for CrewAI:
crewai create crew data_analysis_app
This will create folders for agents, tasks, tools, and crew configuration.

3. Define your Crew and tools
Inside crews/analysis_crew/analysis_crew.py, define your main crew logic using the Crew class.
Custom tools can be created under tools/ for handling data-related tasks.

3. Configure agents and tasks
Use YAML files inside the config/ folder to define your agents and tasks:
config/agents.yaml – define agent roles and behavior
config/tasks.yaml – define tasks, goals, and expected outputs

4. Add your API keys
Create a .env file at the root or in the src/data_analysis_app/ directory, and add:
OPENAI_API_KEY=your-openai-api-key-here

5. Run streamlit run src/data_analysis_app/main.py
   
You can now upload the sample data file and interact with your data.
