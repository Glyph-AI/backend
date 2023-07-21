tagging_prompt = """
CONVERSATION HISTORY: 
{message_history}

CURRENT TAGS: {current_tags}

Provide a list of 5 or less single word tags that represent the topics of this conversation. Do not duplicate topic tags that are already there.

"""