import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from enum import Enum
import json

# Import handlers
from sql_handler import handle_sql_query, load_llm_prompt_data
from api_handler import handle_api_query, load_api_metadata

# Load environment variables from .env
load_dotenv()

# Read API key from .env
api_key = os.getenv("OPENAI_API_KEY")

# Ensure the API key is loaded
if not api_key:
    raise ValueError("⚠️ OPENAI_API_KEY not found in .env file!")

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)

# Define query types as enum for better clarity
class QueryType(str, Enum):
    SQL = "SQL"
    API = "API"
    LLM = "GENERAL"

def route_query(user_query: str) -> QueryType:
    """Route the query to the appropriate system using both SQL and API metadata"""
    # Load both SQL and API metadata
    sql_metadata = load_llm_prompt_data()
    api_metadata = load_api_metadata()
    
    classification_prompt = PromptTemplate(
        input_variables=["query", "sql_metadata", "api_metadata"],
        template="""Given the following information about our SQL database and API capabilities, 
determine which system should handle this user query:

=== SQL DATABASE CAPABILITIES ===
{sql_metadata}

=== API CAPABILITIES ===
{api_metadata}

User Query: "{query}"

Based on the query and available systems, classify this query into exactly one of these categories:
- SQL: If the query is about e-commerce data, product sales, customer information, or other data stored in our SQL database
- API: If the query is about financial markets, stock prices, company financials, or other data available through our Financial API
- GENERAL: If the query doesn't clearly match either system or requires general knowledge

Respond with exactly one word: SQL, API, or GENERAL"""
    )
    
    chain = classification_prompt | llm
    result = chain.invoke({
        "query": user_query,
        "sql_metadata": sql_metadata,
        "api_metadata": api_metadata
    }).content.strip()
    
    return QueryType(result)

def process_query(query_type: QueryType, user_query: str):
    """Process the query based on its type"""
    
    if query_type == QueryType.SQL:
        # Simply handle SQL query without statistical analysis
        handle_sql_query(llm, user_query)
            
    elif query_type == QueryType.API:
        handle_api_query(llm, user_query)
            
    else:  # QueryType.LLM
        print("💭 Using General LLM...")
        response = llm.invoke(user_query)
        print(f"\nResponse:\n{response.content}")

# Main Chat Function
def chat():
    print("\n=== Conversational AI System ===")
    print("Available features:")
    print("1. Sales and returns data queries")
    print("2. Financial market data")
    print("3. General questions")
    print("\nType 'exit' to quit")
    print("=" * 50)

    while True:
        try:
            # Get user input
            user_query = input("\nUser: ").strip()
            
            # Check for exit command
            if user_query.lower() == 'exit':
                print("\nGoodbye! 👋")
                break
                
            # Check for empty input
            if not user_query:
                print("⚠️ Please enter a question or command.")
                continue
                
            # First, route the query to determine the appropriate system
            query_type = route_query(user_query)
            print(f"\n🔍 Route Chosen: {query_type.value}")
            print("=" * 50)
            
            # Process the query using the appropriate system
            process_query(query_type, user_query)
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"\n⚠️ Error: {str(e)}")
            print("=" * 50)
            continue

if __name__ == "__main__":
    chat()
