import os
from pathlib import Path

import click

from eoap_gen.config import WorkflowConfig
from eoap_gen.cwl import (
    cleanup_packed_workflow,
    generate_cwl_cli,
    generate_docker_cli,
    generate_workflow,
    modify_cwl_cli,
    pack_workflow,
    validate_workflow,
    write_cwl_cli_outputs,
)
from eoap_gen.dockerfile import generate_dockerfile, get_requirements
from eoap_gen.utils import create_output_dirs, write_action_output


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(path_type=Path),
    required=True,
)
@click.option(
    "--docker-url-base",
    required=True,
    help=(
        "Base of the docker registry url, e.g. ghcr.io/owner/repo. In combination with "
        "--docker-tag constructs full Docker pull url."
    ),
)
@click.option(
    "--docker-tag",
    required=True,
    help=(
        "Docker image tag, to be used by CWL to pull generated CommandLineTools, e.g. "
        "`main`"
    ),
)
def generate(
    config_path: Path, output_path: Path, docker_url_base: str, docker_tag: str
):
    config = WorkflowConfig.load_config(config_path)

    create_output_dirs(output_path, [s.id_ for s in config.steps])
    for s in config.steps:
        step_output_dir = output_path / "cli" / s.id_
        if s.docker_image:
            generate_docker_cli(s, step_output_dir)
        elif s.script:
            generate_dockerfile(s, step_output_dir)
            write_cwl_cli_outputs(step_output_dir / "tool_out.yml", s.outputs)
            generate_cwl_cli(
                script_path=s.script,
                output_dir=step_output_dir,
                step_id=s.id_,
                requirements=get_requirements(s.requirements),
                cwl_outputs_path=step_output_dir / "tool_out.yml",
            )
            full_docker_url = os.path.join(docker_url_base, f"{s.id_}:{docker_tag}")
            modify_cwl_cli(step_output_dir / f"{s.script.stem}.cwl", full_docker_url, s)
        else:
            raise ValueError(f"Step {s.id_} has no docker image or script.")
    config.set_step_run(output_path / "cli")
    wf_path = output_path / "cli" / "workflow.cwl"
    generate_workflow(config, wf_path)
    packed_wf_path = pack_workflow(wf_path)
    cleanup_packed_workflow(packed_wf_path, config.id_)
    validate_workflow(packed_wf_path)
    write_action_output(config)
