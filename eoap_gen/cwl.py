import os
from pathlib import PurePath, Path
import subprocess
from pathlib import Path, PurePath

from cwl_utils.parser import CommandLineTool, load_document_by_uri, save
from cwl_utils.parser.cwl_v1_0 import DockerRequirement
from ruamel.yaml import YAML

from eoap_gen.template import get_template


def generate_cwl_cli(
    script_path: os.PathLike,
    output_dir: str = "gen-output",
    venv: str | None = None,
    requirements: list[str] = [],
    cwl_outputs_path: os.PathLike | None = None,
):
    if not script_path:
        raise ValueError("Invalid script path.")

    script_name = PurePath(script_path).stem
    if not venv:
        venv = f"{script_name}-venv"

    cmd = get_template("cwltool.jinja").render(
        output_dir=Path(output_dir).resolve(),
        venv=venv,
        requirements=requirements,
        script_path=Path(script_path).resolve(),
        cwl_outputs_path=Path(cwl_outputs_path).resolve() if cwl_outputs_path else None,
    )
    subprocess.run(cmd, shell=True, executable="/bin/bash")


def modify_cwl_cli(cwl_path: os.PathLike, docker_url: str):
    if not cwl_path:
        raise ValueError("Invalid path to cwl file.")
    if not docker_url:
        raise ValueError("Invalid docker image url.")

    tool_obj: CommandLineTool = load_document_by_uri(cwl_path)

    tool_obj.hints = [DockerRequirement(dockerPull=docker_url)]
    tool_obj.baseCommand = ["python", "/app/app.py"]

    tool_dict = save(tool_obj)
    yaml = YAML()
    yaml.default_flow_style = False

    with open(cwl_path, "w") as f:
        yaml.dump(tool_dict, f)
