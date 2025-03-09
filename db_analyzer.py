import sqlite3
import json
from typing import Dict, List, Any

class DatabaseAnalyzer:
    def __init__(self, db_path: str = "ecommerce.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def get_table_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get detailed information about all tables in the database"""
        # Get list of all tables
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            # Get column info for each table
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = self.cursor.fetchall()
            
            # Get foreign key info
            self.cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = self.cursor.fetchall()
            
            # Store column details
            table_info[table_name] = {
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "nullable": not col[3],
                        "primary_key": bool(col[5])
                    } for col in columns
                ],
                "foreign_keys": [
                    {
                        "from": fk[3],
                        "to_table": fk[2],
                        "to_column": fk[4]
                    } for fk in foreign_keys
                ]
            }
        
        return table_info

    def get_table_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics about each table"""
        stats = {}
        for table_name in self.get_tables():
            # Get row count
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = self.cursor.fetchone()[0]
            
            # Get sample values for each column
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
            sample_data = self.cursor.fetchall()
            
            # Get column names
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            stats[table_name] = {
                "row_count": row_count,
                "sample_values": {
                    col: [row[idx] for row in sample_data] 
                    for idx, col in enumerate(columns)
                } if sample_data else {}
            }
        
        return stats

    def get_tables(self) -> List[str]:
        """Get list of all tables"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()]

    def generate_llm_metadata(self) -> str:
        """Generate formatted metadata string for LLM"""
        table_info = self.get_table_info()
        table_stats = self.get_table_statistics()
        
        metadata = ["Database Schema and Statistics:", ""]
        
        # Add relationships overview
        metadata.append("Table Relationships:")
        for table_name, info in table_info.items():
            if info["foreign_keys"]:
                for fk in info["foreign_keys"]:
                    metadata.append(f"- {table_name}.{fk['from']} -> {fk['to_table']}.{fk['to_column']}")
        metadata.append("")
        
        # Add detailed table information
        for table_name in self.get_tables():
            info = table_info[table_name]
            stats = table_stats[table_name]
            
            metadata.append(f"Table: {table_name}")
            metadata.append(f"Total Records: {stats['row_count']}")
            metadata.append("Columns:")
            
            for col in info["columns"]:
                constraints = []
                if col["primary_key"]:
                    constraints.append("PRIMARY KEY")
                if not col["nullable"]:
                    constraints.append("NOT NULL")
                
                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                metadata.append(f"- {col['name']} ({col['type']}){constraint_str}")
            
            # Add sample values if available
            if stats["sample_values"]:
                metadata.append("Sample Values:")
                for col, values in stats["sample_values"].items():
                    unique_values = list(set(str(v) for v in values if v is not None))[:3]
                    if unique_values:
                        metadata.append(f"- {col}: {', '.join(unique_values)}")
            
            metadata.append("")
        
        return "\n".join(metadata)

    def save_metadata_to_file(self, filename: str = "db_metadata.txt"):
        """Save the metadata to a file"""
        metadata = self.generate_llm_metadata()
        with open(filename, 'w') as f:
            f.write(metadata)

    def close(self):
        """Close the database connection"""
        self.conn.close()

def get_db_metadata(db_path: str = "ecommerce.db") -> str:
    """Convenience function to get database metadata"""
    analyzer = DatabaseAnalyzer(db_path)
    metadata = analyzer.generate_llm_metadata()
    analyzer.close()
    return metadata

def save_llm_prompt_data(filename: str = "llm_prompt_data.txt"):
    """Generate and save comprehensive metadata for LLM prompts"""
    analyzer = DatabaseAnalyzer()
    
    prompt_data = """
=== E-commerce Product Database Structure ===

{metadata}

Example Queries:
1. SQL Queries:
   - "Show all products in the Gaming category with price above $1000"
   - "List top 10 products by quantity sold"
   - "Compare sales performance between different categories"
   - "Show monthly sales trends for laptops"

2. Statistical Analysis:
   - "Calculate average order value by category"
   - "Compare product prices across different brands"
   - "Analyze return rates for different product categories"
   - "Show distribution of order amounts"

3. Data Relationships:
   - Products belong to Categories
   - Orders contain multiple Order Items
   - Customers can have multiple Addresses
   - Each Order Item references a Product

SQL Date Functions:
- Use strftime('%Y-%m-%d', date_column) for full date
- Use strftime('%m', date_column) for month
- Use strftime('%Y', date_column) for year
- Example: strftime('%Y-%m', order_date) = '2024-01' for January 2024

Common Aggregations:
- COUNT(*) for counting records
- SUM(quantity * price) for total sales
- AVG(price) for average prices
- GROUP BY category_id, strftime('%Y-%m', order_date) for monthly category reports
"""
    
    # Get database metadata
    metadata = analyzer.generate_llm_metadata()
    
    # Format the complete prompt data
    complete_prompt = prompt_data.format(metadata=metadata)
    
    # Save to file
    with open(filename, 'w') as f:
        f.write(complete_prompt)
    
    analyzer.close()
    return complete_prompt

if __name__ == "__main__":
    # Generate and save both metadata and prompt data
    analyzer = DatabaseAnalyzer()
    analyzer.save_metadata_to_file()
    save_llm_prompt_data()
    analyzer.close() 