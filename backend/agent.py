from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.json_reader import JSONReader
from agno.agent import Agent
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.knowledge import Knowledge
from agno.models.google import Gemini
from agno.vectordb.pgvector import PgVector
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

db_url = "postgresql+psycopg://postgres:password@localhost:5432/agropredict"
vector_db = PgVector(
    table_name="commodities",
    db_url=db_url,
    embedder=GeminiEmbedder(),
)


knowledge = Knowledge(vector_db=vector_db)

agent = Agent(
    model=Gemini(
        id="gemini-2.5-flash-lite", api_key=os.environ.get("GEMINI_API_KEY", "")
    ),
    knowledge=knowledge,
    debug_mode=True,
    search_knowledge=True,
    description="AgroPredict Pro is an AI assistant that provides insights and forecasts on agricultural commodity prices. It can analyze historical data, identify trends, and offer actionable advice to farmers and traders. In case the search results are not relevant, it can generate insights based on its training data and general knowledge of agricultural markets.",
)
