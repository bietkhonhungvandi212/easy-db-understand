from core.database.metadata_extractor import DatabaseMetadataExtractor
from settings_config import settings
from rich.console import Console
from rich.table import Table

def print_dataframe(df, title):
    """Helper function to print DataFrame in a nice format"""
    console = Console()
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print("=" * 80)
    
    if df.empty:
        console.print("[yellow]No data found[/yellow]")
        return
        
    # Create a table
    table = Table(show_header=True, header_style="bold magenta")
    
    # Add columns
    for column in df.columns:
        table.add_column(str(column))
    
    # Add rows
    for _, row in df.iterrows():
        table.add_row(*[str(value) for value in row])
    
    console.print(table)
    console.print(f"Total rows: {len(df)}")

def main():
    """Main function to test database metadata extraction"""
    console = Console()
    console.print("[bold green]🚀 Testing Database Metadata Extractor[/bold green]")
    console.print("=" * 80)
    
    try:
        # Initialize the extractor
        extractor = DatabaseMetadataExtractor()
        
        
        # 1. Test extracting tables
        console.print("\n[bold cyan]1. Testing Table Extraction[/bold cyan]")
        tables_df = extractor.extract_tables()
        print_dataframe(tables_df, "Database Tables")
        
        # 2. Test extracting columns for a specific table
        if not tables_df.empty:
            sample_table = tables_df.iloc[0]['table_name']
            console.print(f"\n[bold cyan]2. Testing Column Extraction for table: {sample_table}[/bold cyan]")
            columns_df = extractor.extract_columns(sample_table)
            print_dataframe(columns_df, f"Columns in {sample_table}")
        
        # 3. Test extracting foreign keys
        console.print("\n[bold cyan]3. Testing Foreign Key Extraction[/bold cyan]")
        foreign_keys_df = extractor.extract_foreign_keys()
        print_dataframe(foreign_keys_df, "Foreign Key Relationships")
        
        # 4. Test finding tables by keyword
        test_keywords = ['user', 'email', 'member', 'company_setup']  # Example keywords
        for keyword in test_keywords:
            console.print(f"\n[bold cyan]4. Testing Table Search for keyword: {keyword}[/bold cyan]")
            tables_by_keyword_df = extractor.find_tables_by_keyword(keyword)
            print_dataframe(tables_by_keyword_df, f"Tables related to '{keyword}'")
        
        console.print("\n[bold green]✅ All tests completed successfully![/bold green]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error during testing: {str(e)}[/bold red]")

if __name__ == "__main__":
    main() 