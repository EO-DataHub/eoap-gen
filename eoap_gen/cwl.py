import json
import shutil
import subprocess
from pathlib import Path

from cwl_utils.parser import CommandLineTool, load_document_by_uri, save
from cwl_utils.parser.cwl_v1_0 import DockerRequirement
from ruamel.yaml import YAML

from eoap_gen.config import StepOutputConfig, WorkflowConfig
from eoap_gen.template import get_template

yaml = YAML()
yaml.default_flow_style = False


def generate_cwl_cli(
    script_path: Path,
    output_dir: Path,
    venv: str | None = None,
    requirements: list[str] = [],
    cwl_outputs_path: Path | None = None,
):
    if not venv:
        venv = f"{script_path.stem}-venv"
    new_script_path = shutil.copy2(script_path, output_dir)
    cmd = get_template("cwltool.jinja").render(
        output_dir=output_dir.resolve(),
        venv=venv,
        requirements=requirements,
        script_path=Path(new_script_path).resolve(),
        cwl_outputs_path=cwl_outputs_path.resolve() if cwl_outputs_path else None,
    )
    res = subprocess.run(cmd, shell=True, executable="/bin/bash", capture_output=True)
    if res.returncode != 0:
        print("Command stdout: ", res.stdout)
        print("Command stderr: ", res.stderr)
        raise RuntimeError("Failed generating cwl CommandLineTool.")


def write_cwl_cli_outputs(path: Path, outputs: list[StepOutputConfig]):
    raw = {"outputs": {}}
    for o in outputs:
        raw["outputs"][o.id_] = o.params
    with open(path, "w") as f:
        yaml.dump(raw, f)


def modify_cwl_cli(cwl_path: Path, docker_url: str):
    tool_obj: CommandLineTool = load_document_by_uri(cwl_path)

    tool_obj.hints = [DockerRequirement(dockerPull=docker_url)]
    tool_obj.baseCommand = ["python", "/app/app.py"]

    tool_dict = save(tool_obj)

    with open(cwl_path, "w") as f:
        yaml.dump(tool_dict, f)


def generate_workflow(config: WorkflowConfig, wf_path: Path):
    wf = config.to_cwl()
    with open(wf_path.resolve(), "w") as f:
        yaml.dump(save(wf, relative_uris=False), f)


def pack_workflow(wf_path: Path):
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
    with open(wf_abs_path.with_stem(f"{wf_abs_path.stem}-packed"), "w") as f:
        yaml.dump(packed_obj, f)


def validate_workflow(wf_path: Path) -> bool:
    abs_path = wf_path.resolve()
    res = subprocess.run(
        f"cwltool --validate {abs_path}",
        shell=True,
        executable="/bin/bash",
    )
    return res.returncode == 0
