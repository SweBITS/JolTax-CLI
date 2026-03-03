import polars as pl
from rich.table import Table
from rich.tree import Tree
from typing import List, Union, Dict

def format_dataframe(df: pl.DataFrame, title: str = "Results") -> Table:
    """Converts a Polars DataFrame into a Rich Table for pretty printing."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns from the DataFrame
    for col in df.columns:
        table.add_column(col)
        
    # Add rows from the DataFrame
    for row in df.iter_rows():
        table.add_row(*[str(val) for val in row])
        
    return table

def format_lineage(lineage_df: pl.DataFrame, target_id: Union[int, str]) -> Tree:
    """Converts a lineage DataFrame into a Rich Tree for visual representation."""
    # Assuming lineage_df is sorted from root to target
    # columns might include tax_id, name, rank
    
    # Create the root of the tree
    if lineage_df.is_empty():
        return Tree(f"[red]No lineage found for {target_id}[/red]")
        
    # Get the first node (root)
    root_row = lineage_df.row(0, named=True)
    root_node = Tree(f"{root_row['name']} ([cyan]{root_row['rank']}[/cyan]) [dim]{root_row['tax_id']}[/dim]")
    
    current_node = root_node
    # Iterate through subsequent nodes
    for i in range(1, len(lineage_df)):
        row = lineage_df.row(i, named=True)
        current_node = current_node.add(f"{row['name']} ([cyan]{row['rank']}[/cyan]) [dim]{row['tax_id']}[/dim]")
        
    return root_node

def format_find_results(df: pl.DataFrame) -> Table:
    """Formats the results of a fuzzy search."""
    return format_dataframe(df, title="Search Results")
