import sys
from .loader import TaxonomyLoader
from .config import load_config
from .shell import JolTaxShell

def main():
    # Load configuration to ensure it and the cache directory exist
    load_config()
    
    loader = TaxonomyLoader()
    shell = JolTaxShell(loader)
    shell.run()

if __name__ == "__main__":
    main()
