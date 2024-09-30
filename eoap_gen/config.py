import os
from pathlib import Path
from typing import Any

from cwl_utils.parser.cwl_v1_0 import (
    InputParameter,
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

    def __init__(self, id_: str, source: str) -> None:
        self.id_ = id_
        self.source = source

    @staticmethod
    def from_dict(d: dict[str, Any]):
        return StepInputConfig(
            id_=d["id"],
            source=d["source"],
        )

    def to_cwl(self):
        return WorkflowStepInput(id=self.id_, source=self.source)


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
    script: Path
    requirements: Path
    inputs: list[StepInputConfig]
    outputs: list[StepOutputConfig]
    run: Path

    def __init__(
        self,
        id_: str,
        script: os.PathLike,
        requirements: os.PathLike,
        inputs: list[StepInputConfig],
        outputs: list[StepOutputConfig],
    ) -> None:
        self.id_ = id_
        self.script = Path(script)
        self.requirements = Path(requirements)
        self.inputs = inputs
        self.outputs = outputs

    @staticmethod
    def from_dict(d: dict[str, Any]):
        inputs_raw = d.get("inputs")
        inputs = []
        if inputs_raw:
            inputs = [StepInputConfig.from_dict(inp) for inp in inputs_raw]

        outputs_raw = d.get("outputs")
        outputs = []
        if outputs_raw:
            outputs = [StepOutputConfig.from_dict(out) for out in outputs_raw]

        return StepConfig(
            id_=d["id"],
            script=d["script"],
            requirements=d["requirements"],
            inputs=inputs,
            outputs=outputs,
        )

    def to_cwl(self):
        return WorkflowStep(
            id=self.id_,
            run=str(self.run.resolve()),
            in_=[inp.to_cwl() for inp in self.inputs],
            out=[out.to_cwl() for out in self.outputs],
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
        )
