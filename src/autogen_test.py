import os
from dotenv import load_dotenv

from autogen import UserProxyAgent, AssistantAgent, GroupChat, GroupChatManager, config_list_from_json
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
# import autogen


load_dotenv()

gpt3_config_list = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST.json",
    file_location= "D:\Projects\curly-carnival\curly-carnival\src",
    filter_dict={
        "model": ["gpt-3.5-turbo-1106"],
    }
)
gpt4_config_list = config_list_from_json(
    env_or_file="OAI_CONFIG_LIST.json",
    file_location= "D:\Projects\curly-carnival\curly-carnival\src",
    filter_dict={
        "model": ["gpt-4-1106-preview"],
    }
)

user = UserProxyAgent(
    name="user", 
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

eve = GPTAssistantAgent(
    name="eve", 
    system_message="""Always answer questions within one sentence. """,
    llm_config={"assistant_id": os.getenv("ASSISTANT_ID"),},
)

gpt_assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": gpt3_config_list,
        "assistant_id": None
    })

groupchat = GroupChat(agents=[user, eve, gpt_assistant], messages=[], max_round=10)
manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config_list)

user.initiate_chat(
    manager,
    message="I need to write an email to apply for a program to study Torah.",
)
