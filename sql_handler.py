import sqlite3
import json
import pandas as pd
from scipy import stats
from langchain.prompts import PromptTemplate
from db_analyzer import get_db_metadata, save_llm_prompt_data

# Initialize database connection
def get_db_connection():
    """Get a connection to the SQLite database"""
    from init_database import init_database
    return init_database()

def load_llm_prompt_data(filename: str = "llm_prompt_data.txt") -> str:
    """Load the LLM prompt data from file"""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️ LLM prompt data file not found, generating new one...")
        return save_llm_prompt_data()

def get_schema_info():
    """Get the database schema information"""
    # Load LLM prompt data
    llm_data = load_llm_prompt_data()

    return f"{llm_data}"

def generate_sql_query(llm, user_query):
    """Generate SQL query from natural language"""
    schema_info = get_schema_info()
    
    sql_prompt = PromptTemplate(
        input_variables=["schema", "query"],
        template="""Given the following SQL table schema:
{schema}

Convert this natural language query into SQL: {query}

Important: Return ONLY the raw SQL query without any markdown formatting, quotes, or explanations.
Example format:
SELECT * FROM table WHERE condition;

Your SQL query:"""
    )
    
    chain = sql_prompt | llm
    return chain.invoke({
        "schema": schema_info,
        "query": user_query
    }).content.strip()

def execute_sql_query(sql_query):
    """Execute SQL query and format results"""
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute(sql_query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        
        if not results:
            return "No results found."
            
        # Format results as a table
        output = "\nResults:\n" + " | ".join(columns) + "\n" + "-" * (len(" | ".join(columns))) + "\n"
        for row in results:
            output += " | ".join(str(item) for item in row) + "\n"
        return output
    except sqlite3.Error as e:
        return f"Error executing SQL query: {str(e)}"

def perform_statistical_analysis(llm, user_query):
    """Perform statistical analysis on query results"""
    schema_info = get_schema_info()
    conn, cursor = get_db_connection()
    
    stats_prompt = PromptTemplate(
        input_variables=["schema", "query"],
        template="""Given the following SQL table schema:
{schema}

Generate a SQL query to get data for statistical analysis for this request: {query}

Important: Return ONLY the raw SQL query without any markdown formatting, quotes, or explanations.
Example format:
SELECT column FROM table WHERE condition;

Your SQL query:"""
    )
    
    # Get data using SQL
    chain = stats_prompt | llm
    sql_query = chain.invoke({
        "schema": schema_info,
        "query": user_query
    }).content.strip()
    
    # Execute SQL and convert to pandas DataFrame
    cursor.execute(sql_query)
    columns = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    df = pd.DataFrame(results, columns=columns)
    
    # Perform statistical analysis
    analysis_results = []
    
    # Basic statistics
    analysis_results.append("Statistical Analysis:")
    
    # Calculate basic metrics for numerical columns
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_columns:
        analysis_results.append(f"\n{col} Statistics:")
        analysis_results.append(f"Mean: {df[col].mean():.2f}")
        analysis_results.append(f"Median: {df[col].median():.2f}")
        analysis_results.append(f"Std Dev: {df[col].std():.2f}")
    
    # If comparing two groups, perform t-test
    if len(df.groupby(df.columns[0])) == 2:
        groups = df.groupby(df.columns[0])
        group1, group2 = [group for _, group in groups]
        for col in numeric_columns:
            t_stat, p_value = stats.ttest_ind(group1[col], group2[col])
            analysis_results.append(f"\nT-test for {col}:")
            analysis_results.append(f"t-statistic: {t_stat:.2f}")
            analysis_results.append(f"p-value: {p_value:.4f}")
    
    return "\n".join(analysis_results)

def analyze_sql_request(llm, user_query):
    """Analyze the SQL request and suggest improvements"""
    schema_info = get_schema_info()
    
    analysis_prompt = PromptTemplate(
        input_variables=["schema", "query"],
        template="""Given this database schema and user request, analyze the query needs:

{schema}

User Request: {query}

Provide a JSON response with:
1. Clarifying questions to improve the query
2. Potential variations of the query
3. Important considerations
4. Suggested filters or conditions

Format your response as a JSON object with these exact keys:
{
    "clarifying_questions": [],
    "query_variations": [],
    "considerations": [],
    "suggested_filters": []
}"""
    )
    
    chain = analysis_prompt | llm
    analysis = json.loads(chain.invoke({
        "schema": schema_info,
        "query": user_query
    }).content.strip())
    
    return analysis

def get_user_preferences(analysis):
    """Get user preferences based on analysis"""
    preferences = {}
    
    print("\n=== Query Analysis ===")
    
    # Ask clarifying questions
    if analysis["clarifying_questions"]:
        print("\nClarifying Questions:")
        for i, question in enumerate(analysis["clarifying_questions"], 1):
            print(f"{i}. {question}")
            answer = input(f"Your answer (press Enter to skip): ").strip()
            if answer:
                preferences[f"answer_{i}"] = answer

    # Show query variations
    if analysis["query_variations"]:
        print("\nPossible Query Variations:")
        for i, variation in enumerate(analysis["query_variations"], 1):
            print(f"{i}. {variation}")
        choice = input("\nSelect variation number (press Enter for default): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(analysis["query_variations"]):
            preferences["selected_variation"] = int(choice)

    # Show important considerations
    if analysis["considerations"]:
        print("\nImportant Considerations:")
        for i, consideration in enumerate(analysis["considerations"], 1):
            print(f"{i}. {consideration}")

    # Ask about suggested filters
    if analysis["suggested_filters"]:
        print("\nSuggested Filters:")
        for i, filter_suggestion in enumerate(analysis["suggested_filters"], 1):
            print(f"{i}. {filter_suggestion}")
            apply = input(f"Apply this filter? (y/n, press Enter to skip): ").lower()
            if apply == 'y':
                preferences[f"filter_{i}"] = True

    return preferences

def generate_improved_sql(llm, user_query, analysis, preferences):
    """Generate improved SQL based on analysis and preferences"""
    schema_info = get_schema_info()
    llm_data = load_llm_prompt_data()
    
    # First generate a basic SQL query to improve upon
    basic_sql = generate_sql_query(llm, user_query)
    
    improvement_prompt = PromptTemplate(
        input_variables=["schema", "query", "analysis", "preferences", "llm_data", "sql_query"],
        template="""Given this database schema, LLM prompt data, and analysis:

Database Schema:
{schema}

LLM Prompt Data:
{llm_data}

Original Request: {query}
Generated SQL: {sql_query}
Analysis: {analysis}
User Preferences: {preferences}

Generate an optimized SQL query that:
1. Incorporates user preferences
2. Includes selected filters
3. Uses appropriate indexing
4. Follows best practices
5. Leverages the database structure described in the LLM prompt data
6. Improves upon the original SQL query where possible

Specifically analyze if the original request could be better answered using information available in the LLM prompt data.

Return ONLY the SQL query without any explanation or markdown."""
    )
    
    chain = improvement_prompt | llm
    return chain.invoke({
        "schema": schema_info,
        "query": user_query,
        "analysis": json.dumps(analysis),
        "preferences": json.dumps(preferences),
        "llm_data": llm_data,
        "sql_query": basic_sql
    }).content.strip()

def validate_sql_query(llm, sql_query):
    """Validate and analyze the generated SQL query"""
    # Load LLM prompt data
    llm_data = load_llm_prompt_data()
    
    # Create a simpler prompt that's more likely to get a valid JSON response
    validation_prompt = PromptTemplate(
        input_variables=["sql", "llm_data"],
        template='''Analyze this SQL query:

{sql}

Database Schema:
{llm_data}

Respond with a JSON object containing these suggestions:
{{
    "strengths": ["strength1", "strength2"],
    "potential_enhancements": ["enhancement1", "enhancement2"],
    "business_considerations": ["consideration1", "consideration2"],
    "suggested_variations": ["variation1", "variation2"]
}}

Your response must be valid JSON.'''
    )
    
    try:
        # Use a simpler approach with fewer variables
        chain = validation_prompt | llm
        response = chain.invoke({
            "sql": sql_query,
            "llm_data": llm_data
        }).content.strip()
        
        # Try to parse the JSON, with multiple fallback approaches
        try:
            # First try direct parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON if there's text before or after
            try:
                # Look for JSON between curly braces
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except:
                # If all parsing fails, create a basic response
                print("\n⚠️ Could not parse LLM response as JSON")
                print("Continuing without validation suggestions.")
                return None
            
    except Exception as e:
        print(f"\n⚠️ Error during query validation: {str(e)}")
        print("Continuing without validation suggestions.")
        return None

def display_sql_validation(validation):
    """Display SQL validation results in a user-friendly format"""
    if not validation:
        return
        
    print("\n=== Query Enhancement Suggestions ===")
    
    if validation.get('strengths'):
        print("\n✅ Current Analysis Provides:")
        for strength in validation['strengths']:
            print(f"  • {strength}")
    
    if validation.get('potential_enhancements'):
        print("\n💡 Could Be Enhanced By:")
        for enhancement in validation['potential_enhancements']:
            print(f"  • {enhancement}")
    
    if validation.get('business_considerations'):
        print("\n🎯 Business Considerations:")
        for consideration in validation['business_considerations']:
            print(f"  • {consideration}")
    
    if validation.get('suggested_variations'):
        print("\n🔄 Alternative Analyses to Consider:")
        for variation in validation['suggested_variations']:
            print(f"  • {variation}")

def process_sql_request(llm, user_query):
    """Process SQL request with analysis and improvements"""
    print("\n=== Processing SQL Request ===")
    print(f"Original request: {user_query}")
    
    # Analyze the request
    analysis = analyze_sql_request(llm, user_query)
    
    # Get user preferences
    preferences = get_user_preferences(analysis)
    
    # Generate improved SQL
    sql_query = generate_improved_sql(llm, user_query, analysis, preferences)
    
    # Validate and analyze the SQL query
    validation = validate_sql_query(llm, sql_query)
    display_sql_validation(validation)
    
    print("\n=== Generated SQL Query ===")
    print(sql_query)
    
    # Ask to proceed or modify based on validation
    if validation and validation.get('potential_enhancements'):
        print("\n⚠️ The generated SQL might need enhancements.")
        choice = input("Would you like to: (1) Proceed anyway, (2) Modify the query, or (3) Cancel? [1/2/3]: ")
        if choice == '2':
            # Allow user to modify the query
            modified_query = input("Enter your modified SQL query:\n")
            if modified_query.strip():
                sql_query = modified_query
        elif choice == '3':
            print("Query cancelled. Please rephrase your request.")
            return None
    else:
        proceed = input("\nProceed with this query? (y/n): ").lower()
        if proceed != 'y':
            print("Query cancelled. Please rephrase your request.")
            return None
    
    return sql_query

def handle_sql_query(llm, user_query):
    """Main handler for SQL queries"""
    print("🗃️ Using SQL Database...")
    
    sql_query = generate_sql_query(llm, user_query)
    print(f"Generated SQL Query: {sql_query}")
    
    # Validate the generated SQL query
    validation = validate_sql_query(llm, sql_query)
    display_sql_validation(validation)
    
    # Only proceed with validation checks if we got a valid response
    if validation:
        # Ask user if they want to proceed with the query
        if validation.get('potential_enhancements'):
            proceed = input("\n⚠️ The query may need enhancements. Proceed anyway? (y/n): ").lower()
            if proceed != 'y':
                print("Query execution cancelled.")
                return
    
    results = execute_sql_query(sql_query)
    print(results) 