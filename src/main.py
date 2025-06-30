import asyncio
from teams.analyzer_gpt import get_analyzer_gpt_team
from agents.data_analyzer_agent import get_data_analyzer_agent
from agents.code_executor_agent import get_code_executor_agent
from conditions.text_mention_termination import get_text_mention_termination
from config.constants import STOP_WORD
from models.openai_model import get_openai_model_client
from config.docker_utils import getDockerCommandLineCodeExecutor, start_docker_container, stop_docker_container
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from dotenv import load_dotenv
import os

async def main(openai_model_client, docker, termination_condition, task_query):
    data_analyzer_agent = get_data_analyzer_agent(openai_model_client)
    code_executor_agent = get_code_executor_agent(docker)

    team = get_analyzer_gpt_team(data_analyzer_agent, code_executor_agent, termination_condition)

    try:
        task = TextMessage(content=task_query, source="user")            

        await start_docker_container(docker)

        async for message in team.run_stream(task=task):
            print("-"*70)
            if isinstance(message, TextMessage):
                print(f"{message.source} : {message.content}")
            elif isinstance(message, TaskResult):
                print(f"Stop Reason: {message.stop_reason}")


    except Exception as e:
        print(f"Error: {e}")
    finally:
        await stop_docker_container(docker)

if __name__=="__main__":
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    asyncio.run(main())