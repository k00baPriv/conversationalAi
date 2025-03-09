import json

def generate_api_metadata():
    """Generate concise metadata about the financial API for LLM routing decisions"""
    
    # Create a simplified version of the API metadata
    api_metadata = {
        "api_name": "Financial Market Data API",
        "description": "API for accessing financial data about companies and markets",
        "capabilities": [
            "Retrieve company financial metrics (revenue, profit, expenses)",
            "Get current stock prices and market capitalization",
            "Access historical performance data",
            "Compare companies within sectors",
            "Track market indices performance"
        ],
        "key_endpoints": [
            {
                "path": "/companies",
                "description": "List all available companies with basic information"
            },
            {
                "path": "/financial-data/{company_id}",
                "description": "Get detailed financial metrics for a specific company"
            },
            {
                "path": "/financial-data",
                "description": "Get summary financial data for all companies"
            },
            {
                "path": "/stock-price/{company_id}",
                "description": "Get historical stock price data for a company"
            },
            {
                "path": "/market-indices",
                "description": "Get data for major market indices like S&P 500, NASDAQ"
            }
        ],
        "supported_companies": [
            {"name": "Apple Inc.", "ticker": "AAPL"},
            {"name": "Microsoft Corp", "ticker": "MSFT"},
            {"name": "Alphabet Inc.", "ticker": "GOOGL"},
            {"name": "Amazon.com Inc.", "ticker": "AMZN"},
            {"name": "Meta Platforms Inc.", "ticker": "META"},
            {"name": "Tesla Inc.", "ticker": "TSLA"},
            {"name": "NVIDIA Corporation", "ticker": "NVDA"},
            {"name": "JPMorgan Chase & Co.", "ticker": "JPM"},
            {"name": "Visa Inc.", "ticker": "V"},
            {"name": "Walmart Inc.", "ticker": "WMT"}
        ],
        "example_queries": [
            "What is Apple's current stock price?",
            "Show me Microsoft's revenue for last year",
            "Compare profit margins between tech companies",
            "How has Tesla's stock performed over the last month?",
            "What are the top performing stocks today?",
            "Show me the current value of the S&P 500",
            "What is the market capitalization of Amazon?",
            "How much did Google's revenue grow last quarter?",
            "What is the P/E ratio for NVIDIA?",
            "Show financial data for all tech companies"
        ]
    }
    
    # Save to file in a format optimized for LLM prompts
    with open("api_metadata.txt", "w") as f:
        f.write("=== Financial Market Data API Capabilities ===\n\n")
        
        f.write(f"{api_metadata['description']}\n\n")
        
        f.write("This API can:\n")
        for capability in api_metadata['capabilities']:
            f.write(f"- {capability}\n")
        f.write("\n")
        
        f.write("Available Endpoints:\n")
        for endpoint in api_metadata['key_endpoints']:
            f.write(f"- {endpoint['path']}: {endpoint['description']}\n")
        f.write("\n")
        
        f.write("Supported Companies:\n")
        companies_text = ", ".join([f"{company['name']} ({company['ticker']})" for company in api_metadata['supported_companies']])
        f.write(f"{companies_text}\n\n")
        
        f.write("Example Financial API Queries:\n")
        for query in api_metadata['example_queries']:
            f.write(f"- \"{query}\"\n")
    
    print(f"Concise API metadata for LLM routing saved to api_metadata.txt")
    return "api_metadata.txt"

if __name__ == "__main__":
    generate_api_metadata() 