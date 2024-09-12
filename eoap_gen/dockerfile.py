import os
from pathlib import Path, PurePath

from eoap_gen.template import get_template


def get_requirements(path: str | os.PathLike | None) -> list[str]:
    if not path:
        return []
    with open(path, "r") as f:
        lines = f.read().splitlines()
    return lines


def get_dockerfile_content(script_name: str, requirements: list[str] = []) -> str:
    return get_template("dockerfile.jinja").render(
        requirements=requirements,
        script_name=script_name,
    )


def save_dockerfile(
    directory: str | os.PathLike, script_name: str, dockerfile_content
) -> None:
    filename = f"{PurePath(script_name).stem}.Dockerfile"
    path = os.path.join(directory, filename)

    with open(path, "w") as f:
        f.write(dockerfile_content.strip())


def generate_dockerfile(script_name: str, reqs_path: Path, save_dir: os.PathLike):
    reqs = get_requirements(reqs_path)
    content = get_dockerfile_content(script_name, reqs)
    save_dockerfile(save_dir, script_name, content)
