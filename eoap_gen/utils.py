import json
import os
from pathlib import Path

from eoap_gen.config import WorkflowConfig


def create_output_dirs(output_path: Path, steps: list[str]):
    os.makedirs(output_path / "cli", exist_ok=True)
    for s in steps:
        os.makedirs(output_path / "cli" / s, exist_ok=True)


def write_action_output(config: WorkflowConfig):
    gh_output = os.getenv("GITHUB_OUTPUT")
    if not gh_output:
        return

    tools = [s.id_ for s in config.steps]

    with open(gh_output, "a") as f:
        print("tools<<EOF", file=f)
        print(json.dumps(tools, separators=(",", ":")), file=f)
        print("EOF", file=f)
