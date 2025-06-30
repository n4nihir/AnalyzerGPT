from autogen_agentchat.conditions import TextMentionTermination

def get_text_mention_termination(text):
    termination_condition = TextMentionTermination(text)

    return termination_condition