from rich.progress import (BarColumn, MofNCompleteColumn, Progress,
                           SpinnerColumn, TaskProgressColumn, TextColumn,
                           TimeRemainingColumn, TimeElapsedColumn)
from rich.table import Column
import time

progress = Progress(
    SpinnerColumn(),
    TextColumn("{task.description}"),
    BarColumn(bar_width=None),
    TaskProgressColumn(),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
    MofNCompleteColumn(),
    expand=True
)

if __name__ == "__main__":
    with progress:
        task1 = progress.add_task("[red]HandBrake [yellow]>> [white]test.mkv", total=2000)

        while not progress.finished:
            progress.update(task1, advance=1)
            time.sleep(0.5)