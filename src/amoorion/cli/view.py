"""What the terminal shows: tables."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from amoorion.core import JsonView, Model, View


class RichView(View):
    """Tables for lists, key/value tables for one model."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    @staticmethod
    def _cell(value: Any) -> str:

        if isinstance(value, bool):
            return "[green]yes[/]" if value else "[red]no[/]"

        if isinstance(value, dict) and isinstance(value.get("text"), str):
            # A message inside a result: what was said, and where.
            return value["text"] + (
                f"\n{value['url']}" if value.get("url") else f"\nid {value.get('id')}"
            )
        
        if isinstance(value, (dict, list)):
            return json.dumps(
                value, 
                ensure_ascii=False
            ) if value else ""
        
        return "" if value is None else str(value)


    def render(self, model: Model | list[Model]) -> None:
        
        rows = JsonView().render(
            model if isinstance(
                model, 
                list
            ) else [model]
        )
        
        if not rows:
            self.console.print(
                "[dim]nothing[/dim]"
            )
            return

        table = Table(
            *rows[0].keys()
        )

        for row in rows:
            table.add_row(
                *(
                    self._cell(value) for value in row.values()
                )
            )
            
        self.console.print(table)
