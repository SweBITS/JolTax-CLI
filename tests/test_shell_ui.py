import polars as pl
from unittest.mock import MagicMock
from joltax_cli.shell import JolTaxShell
from joltax_cli.loader import TaxonomyLoader

def test_shell_commands():
    # Mock JolTree
    mock_tree = MagicMock()
    mock_tree.available_ranks = ["domain", "species"]
    mock_tree.node_count = 1000
    mock_tree.annotate.return_value = pl.DataFrame({
        "tax_id": [123],
        "name": ["TestNode"],
        "rank": ["species"],
        "domain": ["Eukarya"]
    })
    mock_tree.find.return_value = pl.DataFrame({
        "tax_id": [1, 2],
        "name": ["Match1", "Match2"],
        "rank": ["genus", "species"]
    })
    mock_tree.lineage.return_value = pl.DataFrame({
        "tax_id": [1, 10, 123],
        "name": ["Root", "Phylum_A", "TestNode"],
        "rank": ["root", "phylum", "species"]
    })

    # Mock Loader
    mock_loader = MagicMock(spec=TaxonomyLoader)
    mock_loader.list_available_taxonomies.return_value = ["mock_tax"]
    mock_loader.load_taxonomy.return_value = mock_tree

    # Initialize Shell
    shell = JolTaxShell(mock_loader)
    
    # We can't easily run the actual shell loop in a non-interactive test, 
    # but we can test the handlers directly.
    
    print("Testing 'use' command...")
    shell.handle_use(["mock_tax"])
    assert shell.current_name == "mock_tax"
    assert shell.current_tree == mock_tree
    
    print("Testing 'summary' command...")
    shell.handle_summary()
    
    print("Testing 'annotate' command...")
    shell.handle_annotate(["123"])
    mock_tree.annotate.assert_called_with([123])
    
    print("Testing 'find' command...")
    shell.handle_find(["query"])
    mock_tree.find.assert_called_with("query")
    
    print("Testing 'lineage' command...")
    shell.handle_lineage(["123"])
    mock_tree.lineage.assert_called_with(123)
    
    print("All tests passed!")

if __name__ == "__main__":
    test_shell_commands()
