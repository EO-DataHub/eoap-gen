import os
from pathlib import PurePath

from eoap_gen.template import get_template


def get_requirements(path: str | os.PathLike | None) -> list[str]:
    if not path:
        return []
    with open(path, "r") as f:
        lines = f.readlines()
    return lines


def get_dockerfile_content(script_name: str, requirements: list[str] = []) -> str:
    return get_template("dockerfile.jinja").render(
        requirements=requirements,
        script_name=script_name,
    )


def save_dockerfile(
    directory: str | os.PathLike, script_name: str, dockerfile_content
) -> None:
    filename = PurePath(script_name).with_suffix(".Dockerfile")
    path = os.path.join(directory, filename)

    with open(path, "w") as f:
        f.write(dockerfile_content.strip())
