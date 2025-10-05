
from rich import print
from rich.panel import Panel
from rich.console import Console

#[bold], [italic], [underline], [red], [green], [yellow] etc.

console = Console()

print("[bold][italic][underline][red]Test")

console.print(Panel("hello"))