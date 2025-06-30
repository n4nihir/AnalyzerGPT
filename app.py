import streamlit as st
import asyncio
import os
from src.config.constants import WORK_DIR_DOCKER, STOP_WORD
from src.models.openai_model import get_openai_model_client
from src.conditions.text_mention_termination import get_text_mention_termination
from src.config.docker_utils import getDockerCommandLineCodeExecutor, start_docker_container, stop_docker_container
from src.agents.data_analyzer_agent import get_data_analyzer_agent
from src.agents.code_executor_agent import get_code_executor_agent
from src.teams.analyzer_gpt import get_analyzer_gpt_team
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

st.title('Analyzer GPT - Digital Data Analyzer')

uploaded_file = st.file_uploader('Upload your CSV file',type='csv')

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'autogen_team_state' not in st.session_state:
    st.session_state.autogen_team_state = None

task = TextMessage(content=st.text_input("Enter your task",value = 'Can you give me number of columns in my data (file is data.csv)'), source="user")

# task = st.chat_input("Enter your Task.")

async def run_analyzer_gpt(docker,openai_model_client,task):

    try:
        await start_docker_container(docker)

        data_analyzer_agent = get_data_analyzer_agent(openai_model_client)
        code_executor_agent = get_code_executor_agent(docker)
        termination_condition = get_text_mention_termination(STOP_WORD)
        team = get_analyzer_gpt_team(data_analyzer_agent,code_executor_agent,termination_condition)

        if st.session_state.autogen_team_state is not None:
            await team.load_state(st.session_state.autogen_team_state)
        
        
        async for message in team.run_stream(task=task):
            if isinstance(message,TextMessage):
                print(msg := f"{message.source} : {message.content}")
                # yield msg
                if msg.startswith('user'):
                    with st.chat_message('user',avatar='👨'):
                        st.markdown(msg)
                elif msg.startswith('data_analyzer_agent'):
                    with st.chat_message('Data Analyst',avatar='🤖'):
                        st.markdown(msg)                
                elif msg.startswith('code_executor_agent'):
                    with st.chat_message('Code Runner',avatar='🧑🏻‍💻'):
                        st.markdown(msg)
                st.session_state.messages.append(msg)

            elif isinstance(message,TaskResult):
                print(msg:= f"Stop Reason: {message.stop_reason}")
                # yield msg
                st.markdown(msg)
                st.session_state.messages.append(msg)

        st.session_state.autogen_team_state = await team.save_state()
        return None
    except Exception as e:
        print(e)
        return e
    finally:
        await stop_docker_container(docker)
                
if st.session_state.messages:
    for msg in st.session_state.messages:
        st.markdown(msg)


if task:
    if uploaded_file is not None and task:
        
        if not os.path.exists('temp'):
            os.makedirs('temp')

        with open('temp/data.csv','wb') as f:
            f.write(uploaded_file.getbuffer())

    
    openai_model_client = get_openai_model_client()
    docker = getDockerCommandLineCodeExecutor()


    error = asyncio.run(run_analyzer_gpt(docker,openai_model_client,task))

    if error:
        st.error("An error occured :" , {error})

    if os.path.exists('temp/output.png'):
        st.image('temp/output.png',caption='Analysis File')
    
else:
    st.warning("Please upload the csv file")