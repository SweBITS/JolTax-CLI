from pathlib import Path
from typing import List, Optional

try:
    from joltax import JolTree
except ImportError:
    import polars as pl
    # A simple mock to allow basic CLI testing without the backend installed
    class JolTree:
        def __init__(self, tax_dir=None, nodes=None, names=None, path=None):
            self.path = path or tax_dir or nodes
            self.available_ranks = ["domain", "phylum", "class", "order", "family", "genus", "species"]
            self.node_count = 1000
            
        @classmethod
        def load(cls, path):
            return cls(path=path)

        def save(self, directory):
            # Mock save by just ensuring the directory exists
            import os
            os.makedirs(directory, exist_ok=True)
            # Create a dummy metadata file
            with open(os.path.join(directory, "metadata.pkl"), "w") as f:
                f.write("mock metadata")
            
        def annotate(self, ids):
            # Return a dummy DataFrame
            return pl.DataFrame({
                "tax_id": ids,
                "name": [f"Name_{i}" for i in ids],
                "rank": ["species"] * len(ids),
                "domain": ["Eukarya"] * len(ids)
            })
            
        def find(self, query):
            # Return a dummy DataFrame
            return pl.DataFrame({
                "tax_id": [1, 2, 3],
                "name": [f"Result for {query} 1", f"Result for {query} 2", f"Result for {query} 3"],
                "rank": ["genus", "species", "species"]
            })
            
        def lineage(self, tax_id):
            # Return a dummy DataFrame sorted from root to target
            return pl.DataFrame({
                "tax_id": [1, 10, 100, tax_id],
                "name": ["Root", "Phylum_A", "Genus_B", f"Target_{tax_id}"],
                "rank": ["root", "phylum", "genus", "species"]
            })

from .config import get_cache_dir

class TaxonomyLoader:
    def __init__(self):
        self.cache_dir = get_cache_dir()

    def list_available_taxonomies(self) -> List[str]:
        """Scans the cache directory for available taxonomy files/directories."""
        taxonomies = []
        if not self.cache_dir.exists():
            return taxonomies
            
        for item in self.cache_dir.iterdir():
            if item.is_dir():
                taxonomies.append(item.name)
        return taxonomies

    def load_taxonomy(self, name: str) -> Optional['JolTree']:
        """Loads a JolTree instance from the cache directory by name."""
        tax_path = self.cache_dir / name
        if not tax_path.exists():
            print(f"Error: Taxonomy '{name}' not found in cache directory ({self.cache_dir}).")
            return None
        
        try:
            tree = JolTree.load(str(tax_path))
            return tree
        except Exception as e:
            print(f"Error loading taxonomy '{name}': {e}")
            return None

    def build_taxonomy(self, name: str, arg1: str, arg2: Optional[str] = None):
        """Builds a taxonomy from DMP files and saves it to the cache directory."""
        tax_path = self.cache_dir / name
        try:
            if arg2:
                # Assuming arg1 is nodes.dmp and arg2 is names.dmp
                tree = JolTree(nodes=arg1, names=arg2)
            else:
                # Assuming arg1 is tax_dir
                tree = JolTree(tax_dir=arg1)
                
            tree.save(str(tax_path))
            return tax_path
        except Exception as e:
            raise Exception(f"Failed to build taxonomy: {e}")
