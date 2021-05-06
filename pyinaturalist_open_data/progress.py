"""Progress bar configuration"""
from typing import Optional, Tuple

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

ProgressTask = Tuple[Progress, TaskID]


def get_progress(total: int, description: str = 'Loading') -> ProgressTask:
    progress = Progress(
        '[progress.description]{task.description}',
        BarColumn(),
        '[green]{task.completed}/{task.total}',
        '[progress.percentage]{task.percentage:>3.0f}%',
        TimeRemainingColumn(),
    )
    return progress, get_task(progress, total, description)


def get_download_progress(total: int, description: str = 'Downloading') -> ProgressTask:
    progress = Progress(
        '[progress.description]{task.description}',
        BarColumn(),
        '[progress.percentage]{task.percentage:>3.0f}%',
        TransferSpeedColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
    )
    return progress, get_task(progress, total, description)


def get_spinner_progress(description: str = 'Loading') -> Progress:
    progress = Progress('[progress.description]{task.description}', SpinnerColumn(style='green'))
    get_task(progress, None, description)
    return progress


def get_task(progress, total: Optional[int], description: str) -> TaskID:
    return progress.add_task(f'[cyan]{description}...', total=total)
