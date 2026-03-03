import sys
from typing import Optional, List
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.table import Table

from .loader import TaxonomyLoader, JolTree
from .formatter import format_dataframe, format_lineage, format_find_results
from .completer import JolTaxCompleter

class JolTaxShell:
    def __init__(self, loader: TaxonomyLoader):
        self.loader = loader
        self.completer = JolTaxCompleter(loader)
        self.session = PromptSession(
            history=InMemoryHistory(),
            completer=self.completer
        )
        self.console = Console()
        self.current_tree: Optional[JolTree] = None
        self.current_name: Optional[str] = None

    def get_prompt(self) -> str:
        if self.current_name:
            return f"joltax({self.current_name})> "
        return "joltax> "

    def run(self):
        self.console.print("[bold blue]JolTax-CLI Interactive Shell[/bold blue]")
        self.console.print("Type 'help' for commands, 'exit' or Ctrl+D to quit.")

        while True:
            try:
                user_input = self.session.prompt(self.get_prompt()).strip()
                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]

                if command in ("exit", "quit"):
                    break
                elif command == "help":
                    self.show_help()
                elif command == "use":
                    self.handle_use(args)
                elif command == "build":
                    self.handle_build(args)
                elif command == "summary":
                    self.handle_summary()
                elif command == "annotate":
                    self.handle_annotate(args)
                elif command == "find":
                    self.handle_find(args)
                elif command == "lineage":
                    self.handle_lineage(args)
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")

            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[red]Error:[/red] {e}")

        self.console.print("Goodbye!")

    def show_help(self):
        table = Table(title="Available Commands", box=None)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_row("use <name>", "Load a taxonomy from the cache directory.")
        table.add_row("build <name> <tax_dir> [names_dmp]", "Build and save a taxonomy from NCBI DMP files.")
        table.add_row("summary", "Show summary information for the currently loaded taxonomy.")
        table.add_row("annotate <tax_id>...", "Pretty-print canonical ranks for one or more tax IDs.")
        table.add_row("find <query>", "Fuzzy search for tax IDs by name.")
        table.add_row("lineage <tax_id>", "Display the lineage of a tax ID as a visual tree.")
        table.add_row("help", "Show this help message.")
        table.add_row("exit / quit", "Exit the interactive shell.")
        self.console.print(table)

    def _ensure_loaded(self) -> bool:
        if not self.current_tree:
            self.console.print("[yellow]No taxonomy loaded. Use 'use <name>' first.[/yellow]")
            return False
        return True

    def handle_build(self, args):
        if len(args) < 2:
            self.console.print("[yellow]Usage: build <name> <tax_dir> OR build <name> <nodes.dmp> <names.dmp>[/yellow]")
            return
            
        name = args[0]
        arg1 = args[1]
        arg2 = args[2] if len(args) > 2 else None
        
        with self.console.status(f"[bold green]Building taxonomy cache '{name}'... This may take a moment.") as status:
            try:
                tax_path = self.loader.build_taxonomy(name, arg1, arg2)
                self.console.print(f"[green]Successfully built and saved taxonomy '{name}' to {tax_path}.[/green]")
                self.console.print(f"You can now load it using: [cyan]use {name}[/cyan]")
            except Exception as e:
                self.console.print(f"[red]Error building taxonomy:[/red] {e}")

    def handle_use(self, args):
        if not args:
            taxonomies = self.loader.list_available_taxonomies()
            if not taxonomies:
                self.console.print("[yellow]No taxonomies found in cache.[/yellow]")
            else:
                self.console.print("Available taxonomies:")
                for tax in taxonomies:
                    self.console.print(f"  - {tax}")
            return

        name = args[0]
        self.console.print(f"Loading taxonomy '{name}'...")
        tree = self.loader.load_taxonomy(name)
        if tree:
            self.current_tree = tree
            self.current_name = name
            # Update completer with ranks from the new taxonomy
            ranks = getattr(tree, 'available_ranks', [])
            self.completer.set_available_ranks(ranks)
            self.console.print(f"[green]Successfully loaded '{name}'.[/green]")

    def handle_summary(self):
        if not self._ensure_loaded():
            return

        self.console.print(f"[bold underline]Taxonomy Summary: {self.current_name}[/bold underline]")
        # Access actual properties of JolTree if available
        # tree.node_count, tree.version, tree.available_ranks, etc.
        ranks = getattr(self.current_tree, 'available_ranks', [])
        self.console.print(f"Available ranks: [cyan]{', '.join(ranks)}[/cyan]")
        
        # In a real JolTree, we can show node count if it has it
        if hasattr(self.current_tree, 'node_count'):
            self.console.print(f"Node count: {self.current_tree.node_count}")

    def handle_annotate(self, args):
        if not self._ensure_loaded():
            return
        if not args:
            self.console.print("[yellow]Usage: annotate <tax_id> [tax_id...][/yellow]")
            return

        try:
            # Convert string IDs to integers (or leave as strings if JolTree supports both)
            tax_ids = [int(arg) if arg.isdigit() else arg for arg in args]
            df = self.current_tree.annotate(tax_ids)
            
            table = format_dataframe(df, title=f"Annotation for {', '.join(map(str, tax_ids))}")
            with self.console.pager():
                self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error during annotation:[/red] {e}")

    def handle_find(self, args):
        if not self._ensure_loaded():
            return
        if not args:
            self.console.print("[yellow]Usage: find <query>[/yellow]")
            return

        query = " ".join(args)
        try:
            # Check if JolTree has find method
            if not hasattr(self.current_tree, 'find'):
                self.console.print("[red]The find method is not available in the current JolTree version.[/red]")
                return
                
            df = self.current_tree.find(query)
            table = format_find_results(df)
            with self.console.pager():
                self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error during search:[/red] {e}")

    def handle_lineage(self, args):
        if not self._ensure_loaded():
            return
        if not args:
            self.console.print("[yellow]Usage: lineage <tax_id>[/yellow]")
            return

        tax_id = int(args[0]) if args[0].isdigit() else args[0]
        try:
            # Check if JolTree has lineage method
            if not hasattr(self.current_tree, 'lineage'):
                self.console.print("[red]The lineage method is not available in the current JolTree version.[/red]")
                return
                
            df = self.current_tree.lineage(tax_id)
            tree_vis = format_lineage(df, tax_id)
            self.console.print(tree_vis)
        except Exception as e:
            self.console.print(f"[red]Error fetching lineage:[/red] {e}")
