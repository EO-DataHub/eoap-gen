import json
import os
import subprocess
from pathlib import Path, PurePath

from cwl_utils.parser import CommandLineTool, load_document_by_uri, save
from cwl_utils.parser.cwl_v1_0 import DockerRequirement
from ruamel.yaml import YAML

from eoap_gen.template import get_template

yaml = YAML()
yaml.default_flow_style = False


def generate_cwl_cli(
    script_path: os.PathLike,
    output_dir: str = "gen-output",
    venv: str | None = None,
    requirements: list[str] = [],
    cwl_outputs_path: os.PathLike | None = None,
):
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
    res = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True)
    if res.returncode != 0:
        print("Command stdout: ", res.stdout)
        print("Command stderr: ", res.stderr)
        raise RuntimeError("Failed generating cwl CommandLineTool.")


def modify_cwl_cli(cwl_path: os.PathLike, docker_url: str):
    tool_obj: CommandLineTool = load_document_by_uri(cwl_path)

    tool_obj.hints = [DockerRequirement(dockerPull=docker_url)]
    tool_obj.baseCommand = ["python", "/app/app.py"]

    tool_dict = save(tool_obj)

    with open(cwl_path, "w") as f:
        yaml.dump(tool_dict, f)


def pack_workflow(wf_path: os.PathLike):
    wf_abs_path = Path(wf_path).resolve()
    pack_res = subprocess.run(
        f"cwltool --pack {wf_abs_path}",
        shell=True,
        executable="/bin/bash",
        check=True,
        capture_output=True,
    )
    packed_obj = json.loads(pack_res.stdout)
    with open(wf_abs_path.with_stem(f"{wf_abs_path.stem}-packed"), "w") as f:
        yaml.dump(packed_obj, f)


def validate_workflow(wf_path: os.PathLike) -> bool:
    abs_path = Path(wf_path).resolve()
    res = subprocess.run(
        f"cwltool --validate {abs_path}",
        shell=True,
        executable="/bin/bash",
    )
    return res.returncode == 0
