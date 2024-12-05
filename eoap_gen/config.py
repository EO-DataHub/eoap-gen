import os
from pathlib import Path
from typing import Any

from cwl_utils.parser.cwl_v1_0 import (
    InputParameter,
    ScatterFeatureRequirement,
    Workflow,
    WorkflowOutputParameter,
    WorkflowStep,
    WorkflowStepInput,
    WorkflowStepOutput,
)
from ruamel.yaml import YAML


class WorkflowInputConfig:
    id_: str
    label: str
    doc: str
    type_: str
    default: str | None

    def __init__(
        self,
        id_: str,
        type_: str | None = None,
        label: str | None = None,
        doc: str | None = None,
        default: str | None = None,
    ) -> None:
        self.id_ = id_
        self.type_ = type_ or "string"
        self.label = label or doc or id_
        self.doc = doc or label or id_
        self.default = default

    @staticmethod
    def from_dict(d: dict[str, Any]):
        return WorkflowInputConfig(
            id_=d["id"],
            type_=d.get("type"),
            label=d.get("label"),
            doc=d.get("doc"),
            default=d.get("default"),
        )

    def to_cwl(self):
        return InputParameter(
            id=self.id_,
            label=self.label,
            doc=self.doc,
            type_=self.type_,
            default=self.default,
        )


class WorkflowOutputConfig:
    id_: str
    type_: str
    source: list[str]

    def __init__(
        self,
        id_: str,
        source: str | list[str],
        type_: str | None = None,
    ) -> None:
        self.id_ = id_
        self.type_ = type_ or "Directory"
        if isinstance(source, list):
            self.source = source
        else:
            self.source = [source]

    @staticmethod
    def from_dict(d: dict[str, Any]):
        return WorkflowOutputConfig(
            id_=d["id"],
            type_=d.get("type"),
            source=d["source"],
        )

    def to_cwl(self):
        return WorkflowOutputParameter(
            id=self.id_,
            outputSource=self.source,
            type_=self.type_,
        )


class StepInputConfig:
    id_: str
    source: str
    scatter: bool
    value_from: str | None
    default: str | None
    type_: str | None

    def __init__(
        self,
        id_: str,
        source: str,
        scatter: bool = False,
        value_from: str | None = None,
        default: str | None = None,
        type_: str | None = None,
    ) -> None:
        self.id_ = id_
        self.source = source
        self.scatter = scatter
        self.value_from = value_from
        self.default = default
        self.type_ = type_

    @staticmethod
    def from_dict(d: dict[str, Any]):
        return StepInputConfig(
            id_=d["id"],
            source=d["source"],
            scatter=d.get("scatter", False),
            value_from=d.get("value_from"),
            default=d.get("default"),
            type_=d.get("type"),
        )

    def to_cwl(self):
        return WorkflowStepInput(
            id=self.id_,
            source=self.source,
            valueFrom=self.value_from,
            default=self.default,
        )


class StepOutputConfig:
    id_: str
    params: dict[str, Any]

    def __init__(self, id_: str, params: dict[str, Any]) -> None:
        self.id_ = id_
        self.params = params

    @staticmethod
    def from_dict(d: dict[str, Any]):
        params = {k: v for k, v in d.items() if k != "id"}
        return StepOutputConfig(
            id_=d["id"],
            params=params,
        )

    def to_cwl(self):
        return WorkflowStepOutput(id=self.id_)


class StepConfig:
    id_: str
    script: Path | None  # if generating from py script
    requirements: Path | None  # if generating from py script
    apt_install: list[str] | None  # if generating from py script
    docker_image: str | None  # if 3rd party docker image
    command: str | None  # if 3rd party docker image
    inputs: list[StepInputConfig]
    outputs: list[StepOutputConfig]
    scatter_ids: list[str] | None
    scatter_method: str | None
    run: Path

    def __init__(
        self,
        id_: str,
        inputs: list[StepInputConfig],
        outputs: list[StepOutputConfig],
        script: os.PathLike | None = None,
        requirements: os.PathLike | None = None,
        apt_install: list[str] | None = None,
        docker_image: str | None = None,
        command: str | None = None,
        scatter_ids: list[str] | None = None,
        scatter_method: str | None = None,
    ) -> None:
        self.id_ = id_
        self.script = Path(script) if script else None
        self.requirements = Path(requirements) if requirements else None
        self.apt_install = apt_install
        self.docker_image = docker_image
        self.command = command
        self.inputs = inputs
        self.outputs = outputs
        self.scatter_ids = scatter_ids
        if scatter_ids and not scatter_method:
            self.scatter_method = "dotproduct"
        else:
            self.scatter_method = scatter_method

    @staticmethod
    def from_dict(d: dict[str, Any]):
        inputs_raw = d.get("inputs")
        inputs = []
        scatter_ids = None
        if inputs_raw:
            inputs = [StepInputConfig.from_dict(inp) for inp in inputs_raw]
            scatter_ids = [inp.id_ for inp in inputs if inp.scatter]
        outputs_raw = d.get("outputs")
        outputs = []
        if outputs_raw:
            outputs = [StepOutputConfig.from_dict(out) for out in outputs_raw]

        return StepConfig(
            id_=d["id"],
            script=d.get("script"),
            requirements=d.get("requirements"),
            apt_install=d.get("apt_install"),
            docker_image=d.get("docker_image"),
            command=d.get("command"),
            inputs=inputs,
            outputs=outputs,
            scatter_ids=scatter_ids,
            scatter_method=d.get("scatter_method"),
        )

    def to_cwl(self):
        return WorkflowStep(
            id=self.id_,
            run=str(self.run.resolve()),
            in_=[inp.to_cwl() for inp in self.inputs],
            out=[out.to_cwl() for out in self.outputs],
            scatter=self.scatter_ids or None,
            scatterMethod=self.scatter_method,
        )


class WorkflowConfig:
    id_: str
    doc: str
    label: str
    inputs: list[WorkflowInputConfig]
    outputs: list[WorkflowOutputConfig]
    steps: list[StepConfig]

    def __init__(
        self,
        id_: str,
        inputs: list[WorkflowInputConfig],
        outputs: list[WorkflowOutputConfig],
        steps: list[StepConfig],
        doc: str | None = None,
        label: str | None = None,
    ) -> None:
        self.id_ = id_
        self.doc = doc or label or id_
        self.label = label or doc or id_
        self.inputs = inputs
        self.outputs = outputs
        self.steps = steps

    @staticmethod
    def from_dict(d: dict[str, Any]):
        inputs_raw = d.get("inputs")
        inputs = []
        if inputs_raw:
            inputs = [WorkflowInputConfig.from_dict(inp) for inp in inputs_raw]

        outputs = [WorkflowOutputConfig.from_dict(out) for out in d["outputs"]]

        steps = [StepConfig.from_dict(s) for s in d["steps"]]

        return WorkflowConfig(
            id_=d["id"],
            doc=d.get("doc"),
            label=d.get("label"),
            inputs=inputs,
            outputs=outputs,
            steps=steps,
        )

    @staticmethod
    def load_config(path: os.PathLike):
        yaml = YAML()
        yaml.default_flow_style = False
        raw = yaml.load(Path(path))
        return WorkflowConfig.from_dict(raw)

    def set_step_run(self, cli_dir: Path):
        for step in self.steps:
            step.run = cli_dir / step.id_ / f"{step.id_}.cwl"

    def to_cwl(self):
        return Workflow(
            id=self.id_,
            doc=self.doc,
            label=self.label,
            inputs=[inp.to_cwl() for inp in self.inputs],
            outputs=[out.to_cwl() for out in self.outputs],
            steps=[step.to_cwl() for step in self.steps],
            cwlVersion="v1.0",
            requirements=[ScatterFeatureRequirement()],
        )
