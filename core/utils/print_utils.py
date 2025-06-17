from typing import List, Dict, Any
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

def print_dict_list(dict_list: List[Dict[str, Any]], title: str = "Data List") -> None:
    """
    Print a list of dictionaries in a readable format using Rich console.
    
    Args:
        dict_list (List[Dict[str, Any]]): The list of dictionaries to print
        title (str): Title for the output panel
    """
    if not dict_list:
        console.print("[yellow]No data found[/yellow]")
        return
    
    # Create a panel for each item
    for i, item in enumerate(dict_list, 1):
        # Convert dict to formatted JSON string
        json_str = json.dumps(item, indent=2)
        # Create syntax-highlighted JSON
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        # Create panel with title
        panel = Panel(syntax, title=f"Item {i}", border_style="blue")
        console.print(panel)

def print_dict_list_json(dict_list: List[Dict[str, Any]], title: str = "JSON Output") -> None:
    """
    Print a list of dictionaries in JSON format using Rich console.
    
    Args:
        dict_list (List[Dict[str, Any]]): The list of dictionaries to print
        title (str): Title for the output panel
    """
    if not dict_list:
        console.print("[yellow]No data found[/yellow]")
        return
    
    # Convert entire list to formatted JSON string
    json_str = json.dumps(dict_list, indent=2)
    # Create syntax-highlighted JSON
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    # Create panel with title
    panel = Panel(syntax, title=title, border_style="green")
    console.print(panel)

def print_dict_list_table(dict_list: List[Dict[str, Any]], title: str = "Data Table") -> None:
    """
    Print a list of dictionaries in a table format using Rich console.
    
    Args:
        dict_list (List[Dict[str, Any]]): The list of dictionaries to print
        title (str): Title for the table
    """
    if not dict_list:
        console.print("[yellow]No data found[/yellow]")
        return
    
    # Get all unique keys from all dictionaries
    all_keys = set()
    for item in dict_list:
        all_keys.update(item.keys())
    
    # Convert to sorted list for consistent column order
    headers = sorted(list(all_keys))
    
    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns
    for key in headers:
        table.add_column(str(key))
    
    # Add rows
    for item in dict_list:
        row = []
        for key in headers:
            value = item.get(key, "")
            # Convert value to string and truncate if too long
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            row.append(value_str)
        table.add_row(*row)
    
    # Print table
    console.print(table)
    console.print(f"[bold blue]Total items: {len(dict_list)}[/bold blue]")

def print_dict_list_summary(dict_list: List[Dict[str, Any]], title: str = "Data Summary") -> None:
    """
    Print a summary of the dictionary list including key statistics.
    
    Args:
        dict_list (List[Dict[str, Any]]): The list of dictionaries to print
        title (str): Title for the summary
    """
    if not dict_list:
        console.print("[yellow]No data found[/yellow]")
        return
    
    # Get all unique keys
    all_keys = set()
    for item in dict_list:
        all_keys.update(item.keys())
    
    # Create summary table
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    
    # Add summary rows
    table.add_row("Total Items", str(len(dict_list)))
    table.add_row("Total Unique Keys", str(len(all_keys)))
    table.add_row("Keys", ", ".join(sorted(all_keys)))
    
    # Add value type distribution
    type_distribution = {}
    for item in dict_list:
        for key, value in item.items():
            type_name = type(value).__name__
            type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
    
    table.add_row("Value Types", ", ".join(f"{k}: {v}" for k, v in type_distribution.items()))
    
    console.print(table) 