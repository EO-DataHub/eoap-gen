import os
from pathlib import PurePath, Path
import subprocess
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


