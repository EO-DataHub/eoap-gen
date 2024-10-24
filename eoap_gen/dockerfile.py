import os
from pathlib import Path

from eoap_gen.config import StepConfig
from eoap_gen.template import get_template


def get_requirements(path: Path | None) -> list[str]:
    if not path:
        return []
    with open(path, "r") as f:
        lines = f.read().splitlines()
    return lines


def get_dockerfile_content(script_path: Path, requirements: list[str] = []) -> str:
    return get_template("dockerfile.jinja").render(
        requirements=requirements,
        script_name=script_path.name,
    )


def save_dockerfile(
    directory: Path,
    script_path: Path,
    step_id: str,
    dockerfile_content: str,
) -> None:
    filename = f"{step_id}.Dockerfile"
    path = os.path.join(directory, filename)

    with open(path, "w") as f:
        f.write(dockerfile_content.strip())


def generate_dockerfile(step: StepConfig, save_dir: Path):
    reqs = get_requirements(step.requirements)
    content = get_dockerfile_content(step.script, reqs)
    save_dockerfile(save_dir, step.script, step.id_, content)
