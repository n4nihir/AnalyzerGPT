from autogen_agentchat.teams import RoundRobinGroupChat

def get_analyzer_gpt_team(data_analyzer_agent, code_executor_agent, termination_condition):

    analyzer_gpt_team = RoundRobinGroupChat(
        participants= [data_analyzer_agent, code_executor_agent],
        max_turns= 10,
        termination_condition= termination_condition
    )
    return analyzer_gpt_team