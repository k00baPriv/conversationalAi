import requests
import json
from langchain.prompts import PromptTemplate

def normalize_company_name(company_name: str) -> str:
    """Normalize company name to match API format."""
    company_mapping = {
        "apple": "Apple Inc.",
        "microsoft": "Microsoft Corp",
        # Add more mappings as needed
    }
    
    # Clean and normalize the input
    cleaned_name = company_name.lower().strip()
    
    # Check for exact matches in mapping
    for key, value in company_mapping.items():
        if key in cleaned_name:
            return value
            
    # If no match found, try to append Inc./Corp
    if "microsoft" in cleaned_name or "msft" in cleaned_name:
        return "Microsoft Corp"
    if "apple" in cleaned_name:
        return "Apple Inc."
        
    # If still no match, return original (will likely result in 404)
    return company_name

def extract_company_name(user_query: str) -> str:
    """Extract company name from user query."""
    # This is a simplified version - in a real app, you'd use NLP
    common_companies = ["apple", "microsoft", "google", "amazon", "tesla"]
    
    for company in common_companies:
        if company.lower() in user_query.lower():
            return normalize_company_name(company)
    
    return "NONE"  # Indicates no specific company found

def call_financial_api(company_name=None):
    """Call the financial API to get data."""
    # In a real app, this would make an actual API call
    # For this example, we'll simulate the API response
    
    if company_name and company_name != "NONE":
        # Simulate API call for specific company
        try:
            # In a real app, this would be:
            # response = requests.get(f"https://api.example.com/financial-data/{company_name}")
            # return response.json()
            
            # For this example, return mock data
            return {
                "company_name": company_name,
                "financial_metrics": {
                    "revenue": "$365.8B",
                    "profit_margin": "25.9%",
                    "operating_expenses": "$87.5B",
                    "cash_flow": "$111.4B"
                },
                "stock_data": {
                    "current_price": "$182.63",
                    "market_cap": "$2.87T",
                    "pe_ratio": "30.42",
                    "dividend_yield": "0.5%"
                },
                "historical_performance": {
                    "revenue_growth": "7.8%",
                    "profit_growth": "5.2%",
                    "previous_year_revenue": "$338.5B",
                    "previous_year_profit": "$94.7B"
                },
                "last_updated": "2023-06-15T14:30:00Z"
            }
        except Exception as e:
            return f"Error fetching data for {company_name}: {str(e)}"
    else:
        # Simulate API call for all companies
        try:
            # In a real app, this would be:
            # response = requests.get("https://api.example.com/financial-data")
            # return response.json()
            
            # For this example, return mock data for multiple companies
            return [
                {
                    "company_name": "Apple Inc.",
                    "financial_metrics": {
                        "revenue": "$365.8B",
                        "profit_margin": "25.9%"
                    }
                },
                {
                    "company_name": "Microsoft Corp",
                    "financial_metrics": {
                        "revenue": "$198.3B",
                        "profit_margin": "36.5%"
                    }
                },
                # Add more companies as needed
            ]
        except Exception as e:
            return f"Error fetching financial data: {str(e)}"

def format_api_response(api_data, user_query):
    """Format API response based on user query."""
    # For a single company
    if isinstance(api_data, dict):
        company = api_data["company_name"]
        output = f"Financial Data for {company}:\n\n"
        
        # Add financial metrics
        output += "Financial Metrics:\n"
        for key, value in api_data["financial_metrics"].items():
            output += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        # Add stock data
        output += "\nStock Data:\n"
        for key, value in api_data["stock_data"].items():
            output += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        # Add historical performance
        output += "\nHistorical Performance:\n"
        for key, value in api_data["historical_performance"].items():
            output += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        output += f"\nLast Updated: {api_data['last_updated']}"
        return output
    
    # For multiple companies
    elif isinstance(api_data, list):
        output = "Financial Data Summary:\n\n"
        for company in api_data:
            output += f"{company['company_name']}:\n"
            for key, value in company["financial_metrics"].items():
                output += f"  • {key.replace('_', ' ').title()}: {value}\n"
            output += "\n"
        return output
    
    # For error messages
    else:
        return api_data

def handle_api_query(llm, user_query):
    """Main handler for API queries"""
    print("📊 Using Financial API...")
    company_name = extract_company_name(user_query)
    
    if company_name.upper() == "NONE":
        print("ℹ️ Fetching data for all companies")
        api_data = call_financial_api()
    else:
        print(f"ℹ️ Fetching data for: {company_name}")
        api_data = call_financial_api(company_name)
    
    if isinstance(api_data, str) and "Error" in api_data:
        print(f"\n⚠️ {api_data}")
    else:
        formatted_response = format_api_response(api_data, user_query)
        print("\nResponse:")
        print("-" * 50)
        print(formatted_response)

def load_api_metadata(filename: str = "api_metadata.txt") -> str:
    """Load the API metadata from file"""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️ API metadata file not found, generating new one...")
        from api_metadata import generate_api_metadata
        filename = generate_api_metadata()
        with open(filename, 'r') as f:
            return f.read()

def get_api_info():
    """Get the API information"""
    # Load API metadata
    api_metadata = load_api_metadata()
    return api_metadata 