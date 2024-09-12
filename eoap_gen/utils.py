import os
from pathlib import Path


def create_output_dirs(output_path: Path, steps: list[str]):
    os.makedirs(output_path / "cli", exist_ok=True)
    for s in steps:
        os.makedirs(output_path / "cli" / s, exist_ok=True)
