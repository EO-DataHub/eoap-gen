import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from cwl_utils.parser import load_document_by_uri, save
from cwl_utils.parser.cwl_v1_0 import (
    CommandInputParameter,
    CommandLineBinding,
    CommandLineTool,
    DockerRequirement,
    InlineJavascriptRequirement,
)
from ruamel.yaml import YAML

from eoap_gen.config import StepConfig, StepOutputConfig, WorkflowConfig
from eoap_gen.template import get_template

yaml = YAML()
yaml.default_flow_style = False


def generate_cwl_cli(
    script_path: Path,
    output_dir: Path,
    step_id: str,
    venv: str | None = None,
    requirements: list[str] = [],
    cwl_outputs_path: Path | None = None,
    conda_pkgs: list[str] | None = None,
    python_version: str | None = None,
):
    if not venv:
        venv = f"{step_id}-venv"

    if conda_pkgs:
        conda_env = venv
    else:
        conda_env = None
    new_script_path = shutil.copy2(script_path, output_dir)
    cmd = get_template("cwltool.jinja").render(
        output_dir=output_dir.resolve(),
        venv=venv,
        requirements=requirements,
        script_path=Path(new_script_path).resolve(),
        cwl_outputs_path=cwl_outputs_path.resolve() if cwl_outputs_path else None,
        conda_env=conda_env,
        conda_pkgs=conda_pkgs,
        python_version=python_version,
    )
    res = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True)
    if res.returncode != 0:
        print("Command stdout: ", res.stdout)
        print("Command stderr: ", res.stderr)
        raise RuntimeError("Failed generating cwl CommandLineTool.")


def generate_docker_cli(step: StepConfig, output_dir: Path) -> None:
    if not step.command:
        raise ValueError(f"Step {step.id_} has no command.")
    command_parts = step.command.split()
    base_command = []
    inputs = []
    outputs = {o.id_: o.params for o in step.outputs}
    base_command_complete = False
    next_prefix = None

    # regex to find ${...} patterns
    pattern = re.compile(r"(\S+)?\$\{([^}]+)\}")
    for i, part in enumerate(command_parts):
        re_match = re.match(pattern, part)
        if not base_command_complete and not re_match:
            base_command.append(part)
        elif re_match:
            base_command_complete = True
            prefix = re_match.group(1)
            if prefix and next_prefix:
                prefix = f"{next_prefix} {prefix}"
            inp_id = re_match.group(2)
            inp_config = next((i for i in step.inputs if i.id_ == inp_id), None)
            if not inp_config:
                raise ValueError(f"Step {step.id_} has no input {inp_id}.")
            inp = CommandInputParameter(
                id=inp_id,
                type_="string",
                inputBinding=CommandLineBinding(
                    position=i,
                    prefix=prefix or next_prefix,
                    separate=True if next_prefix and not prefix else False,
                    valueFrom=inp_config.value_from,
                ),
            )
            if inp_config:
                inp.default = inp_config.default
            inputs.append(inp)
            next_prefix = None
        else:
            next_prefix = part

    tool_obj = CommandLineTool(
        baseCommand=command_parts[0],
        requirements=[
            DockerRequirement(dockerPull=step.docker_image),
            InlineJavascriptRequirement(),
        ],
        inputs=inputs,
        outputs=outputs,
        cwlVersion="v1.0",
    )

    tool_dict = save(tool_obj)
    with open(output_dir / f"{step.id_}.cwl", "w") as f:
        yaml.dump(tool_dict, f)


def write_cwl_cli_outputs(path: Path, outputs: list[StepOutputConfig]):
    raw = {"outputs": {}}
    for o in outputs:
        raw["outputs"][o.id_] = o.params
    with open(path, "w") as f:
        yaml.dump(raw, f)


def modify_cwl_cli(cwl_path: Path, docker_url: str, step: StepConfig):
    new_path = cwl_path.with_stem(step.id_)
    os.rename(cwl_path, new_path)
    tool_obj: CommandLineTool = load_document_by_uri(new_path)

    tool_obj.requirements = [
        DockerRequirement(dockerPull=docker_url),
        InlineJavascriptRequirement(),
    ]

    tool_obj.baseCommand = ["python", "/app/app.py"]
    if step.conda:
        # if using micromamba, need to run the entrypoint script explicitly
        tool_obj.baseCommand.insert(0, "/usr/local/bin/_entrypoint.sh")

    for inp in step.inputs:
        if inp.type_:
            inp_config = next(
                (i for i in tool_obj.inputs if f"#{inp.id_}" in i.id), None
            )
            if not inp_config:
                raise ValueError(f"Step {step.id_} has no input {inp.id_}.")
            inp_config.type_ = inp.type_

    tool_dict = save(tool_obj)

    with open(new_path, "w") as f:
        yaml.dump(tool_dict, f)


def generate_workflow(config: WorkflowConfig, wf_path: Path):
    wf = config.to_cwl()
    with open(wf_path.resolve(), "w") as f:
        yaml.dump(save(wf, relative_uris=False), f)


def pack_workflow(wf_path: Path) -> Path:
    wf_abs_path = wf_path.resolve()
    pack_res = subprocess.run(
        f"cwltool --pack {wf_abs_path}",
        shell=True,
        executable="/bin/bash",
        capture_output=True,
    )
    if pack_res.returncode != 0:
        print("Command stdout: ", pack_res.stdout)
        print("Command stderr: ", pack_res.stderr)
        raise RuntimeError("Failed packing workflow.")
    packed_obj = json.loads(pack_res.stdout)
    packed_path = wf_abs_path.with_stem(f"{wf_abs_path.stem}-packed")
    with open(packed_path, "w") as f:
        yaml.dump(packed_obj, f)
    return packed_path


def cleanup_packed_workflow(packed_path: Path, wf_id: str):
    res = subprocess.run(
        f"sed -i 's/\\([^ ]*\\)\\.cwl/\\1/g' {packed_path}",
        shell=True,
        executable="/bin/bash",
    )
    if res.returncode != 0:
        print("Command stdout: ", res.stdout)
        print("Command stderr: ", res.stderr)
        raise RuntimeError("Failed cleaning up packed workflow.")

    res = subprocess.run(
        f"sed -i 's/#main/#{wf_id}/g' {packed_path}",
        shell=True,
        executable="/bin/bash",
    )
    if res.returncode != 0:
        print("Command stdout: ", res.stdout)
        print("Command stderr: ", res.stderr)
        raise RuntimeError("Failed cleaning up packed workflow.")


def validate_workflow(wf_path: Path) -> bool:
    abs_path = wf_path.resolve()
    res = subprocess.run(
        f"cwltool --validate {abs_path}",
        shell=True,
        executable="/bin/bash",
    )
    return res.returncode == 0
