from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
import chainlit as cl
import json

cloud_config= {
  'secure_connect_bundle': 'scb.zip'
}

with open("token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = "live"
OPENAI_API_KEY = secrets["openai"]

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
cassSession = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=cassSession,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = """
You are now the guide of a mystical journey in the Whispering Woods. 
A traveler named Elara seeks the lost Gem of Serenity. 
You must navigate her through challenges, choices, and consequences, 
dynamically adapting the tale based on the traveler's decisions. 
Your goal is to create a branching narrative experience where each choice 
leads to a new path, ultimately determining Elara's fate. 

Here are some rules to follow:
1. Start by asking the player to choose some kind of weapon that will be used later in the game
2. Have a few paths that lead to success
3. Have some paths that lead to death. If the user dies generate a response that explains the death and ends in the text: "The End.", I will search for this text to end the game

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:"""
@cl.on_chat_start
async def main():
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input"],
        template=template
    )
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=cass_buff_memory,
        verbose=True
    )
    cl.user_session.set("llm_chain", llm_chain)
    await cl.Message("Welcome to Astra DB Choose Your Own Adventure. Type 'start' to begin.").send()

    
@cl.on_message
async def main(choice: cl.Message):
    llm_chain = cl.user_session.get("llm_chain")
    response = await llm_chain.acall(choice.content, callbacks=[cl.AsyncLangchainCallbackHandler()])
    await cl.Message(content=response["text"]).send()