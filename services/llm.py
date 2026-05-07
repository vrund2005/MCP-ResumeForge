from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm1 = ChatGroq(model="openai/gpt-oss-120b")
llm2 = ChatGroq(model="openai/gpt-oss-20b")
model = ChatGroq(model="llama-3.3-70b-versatile")