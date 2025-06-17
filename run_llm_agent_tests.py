import pytest
import os
from dotenv import load_dotenv
from rich.console import Console

console = Console()

def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure required environment variables are set
    required_vars = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "VECTOR_STORE_PERSIST_DIRECTORY",
        "VECTOR_STORE_COLLECTION_NAME",
        "VECTOR_STORE_EMBEDDING_MODEL",
        "LLM_BASE_URL",
        "LLM_API_KEY",
        "LLM_MODEL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        console.print("[bold red]Error: Missing required environment variables:[/bold red]")
        for var in missing_vars:
            console.print(f"  - {var}")
        return 1
    
    console.print("[bold green]🚀 Running LLM Agent Tests[/bold green]")
    console.print("=" * 80)
    
    # Run the tests
    pytest.main([
        "tests/test_llm_agent.py",
        "-v",  # verbose output
        "--capture=no"  # show print statements
    ])

if __name__ == "__main__":
    exit(main()) 