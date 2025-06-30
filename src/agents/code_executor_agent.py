from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
import asyncio
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

def get_code_executor_agent(code_executor):
        
    code_executor_agent= CodeExecutorAgent(
            name= "code_executor_agent",
            code_executor= code_executor
        )
    
    return code_executor_agent

async def main():
    docker= DockerCommandLineCodeExecutor(
        work_dir= "docker_temp",
        timeout= 120
    )

    await docker.start()
    code_executor_agent= get_code_executor_agent(docker)

    task= TextMessage(content= '''Here is the Python Code which you have to run.
```python
print("Hello, World!")```
''', source= "user")

    try:
        res = await code_executor_agent.on_messages(
                messages=[task], 
                cancellation_token=CancellationToken()
            )
        print(f"Result: {res}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await docker.stop()

if __name__ == "__main__":
    asyncio.run(main())