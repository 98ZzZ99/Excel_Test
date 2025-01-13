import os
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "sk-proj-**********"

# Import Tool from our custom tool file excel_tools.py
from tools.excel_tools import load_excel_data_tool, get_top_bottom_kpi_tool


def main():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    # Initialize LLM. Here we use gpt-3.5-turbo. If you need to change it, you can change it to other models.
    llm = ChatOpenAI(
        temperature=0.3,
        openai_api_key=openai_api_key,
        model_name="gpt-3.5-turbo"
    )

    # Package Tools into a list
    custom_tools = [
        load_excel_data_tool,
        get_top_bottom_kpi_tool,
    ]

    # Building a "Tool Agent"
    #    Execute the agent work and pass the tool into
    agent = initialize_agent(
        tools=custom_tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Demo Dialogue Inquiry
    input_str = "file_path=E:/LLMTest/Test.xlsx; worker_id=23456"    # Your Excel file path
    response = agent.run(input_str)
    print(response)

    # When calling the tool, the input parameters need to be changed to a single string format!!!
    # # Test whether Agent+Tools works properly
    # file_path = "E:/LLMTest/Test.xlsx"  # Your Excel file path
    #
    # # a) Ask job information of all workers
    # user_question_1 = f"Please help me get job information of all workers from {file_path}，including ID、start、end、work、KPI."
    # print("User:", user_question_1)
    # response_1 = agent.run(user_question_1)
    # print("Agent:", response_1)
    #
    # # b) Query the KPI and working hours of worker with ID 23456
    # user_question_2 = f"Tell me the specific information of the worker with ID 23456, obtained from {file_path}."
    # print("\nUser:", user_question_2)
    # response_2 = agent.run(user_question_2)
    # print("Agent:", response_2)
    #
    # # c) Ask the top three and bottom three KPIs
    # user_question_3 = f"List the three workers with the highest KPI and the three workers with the lowest KPI. File path: {file_path}."
    # print("\nUser:", user_question_3)
    # response_3 = agent.run(user_question_3)
    # print("Agent:", response_3)


if __name__ == "__main__":
    main()


