from typing import Iterable, List, Optional
from prompt_toolkit.completion import Completer, Completion, CompleteEvent
from prompt_toolkit.document import Document

from .loader import TaxonomyLoader

class JolTaxCompleter(Completer):
    def __init__(self, loader: TaxonomyLoader):
        self.loader = loader
        self.commands = ["use", "build", "summary", "annotate", "find", "lineage", "help", "exit", "quit"]
        self.current_ranks: List[str] = []

    def set_available_ranks(self, ranks: List[str]):
        """Sets the available ranks for the currently loaded taxonomy."""
        self.current_ranks = ranks

    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor
        parts = text_before_cursor.split()
        
        # 1. Complete top-level commands if we are at the beginning of the line
        if len(parts) == 0 or (len(parts) == 1 and not text_before_cursor.endswith(" ")):
            word_to_complete = parts[0] if parts else ""
            for cmd in self.commands:
                if cmd.startswith(word_to_complete):
                    yield Completion(cmd, start_position=-len(word_to_complete))
            return
            
        # 2. Command-specific completions
        command = parts[0].lower()
        
        # Complete 'use <name>'
        if command == "use" and len(parts) <= 2:
            word_to_complete = parts[1] if len(parts) == 2 else ""
            if not text_before_cursor.endswith(" ") or len(parts) == 1:
                # If we are completing the first arg
                taxonomies = self.loader.list_available_taxonomies()
                for tax in taxonomies:
                    if tax.startswith(word_to_complete):
                        yield Completion(tax, start_position=-len(word_to_complete))
                        
        # Complete other commands could go here (e.g., annotate might complete IDs from a local list? 
        # But that's probably overkill for now).
        # We could use self.current_ranks for something in the future.
