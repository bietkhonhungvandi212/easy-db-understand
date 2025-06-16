import pytest
import os
from dotenv import load_dotenv

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
        "VECTOR_STORE_EMBEDDING_MODEL"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return 1
    
    # Run the tests
    pytest.main([
        "tests/test_vector_store.py",
        "-v",  # verbose output
        "--capture=no"  # show print statements
    ])

if __name__ == "__main__":
    exit(main()) 