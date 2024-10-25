# EOAP-GEN

[![codecov](https://codecov.io/gh/EO-DataHub/eoap-gen/graph/badge.svg?token=8SPB2DV06P)](https://codecov.io/gh/EO-DataHub/eoap-gen)
A CLI tool for generating Earth Observation Application Packages including CWL workflows and Dockerfiles from user supplied python scripts.

# Usage

## Requirements

- Python scripts using argparse or click. Parameters are mapped to CWL CommandLineTool inputs
- Pip requirements file for each script
- eoap-gen configuration file

## Configuration

EOAP-GEN requires a yaml formatted configuration file. This configuration contains certain setting for CWL and especially the flow of data between user inputs, workflow steps and wf output. For more EODH ADES specific guidance see this [tutorial]().

Example of a single step configuration

```yaml
id: resize-collection
doc: Resize collection cogs
label: Resize collection cogs
inputs:
  - id: catalog
    label: catalog
    doc: full catalog path
    type: string
    default: supported-datasets/ceda-stac-fastapi
  - id: collection
    label: collection id
    doc: collection id
    type: string
    default: sentinel2_ard
outputs:
  - id: stac_output
    type: Directory
    source: step3/stac_catalog
steps:
  - id: get_urls
    script: playground/get_urls.py
    requirements: playground/get_urls_reqs.txt
    inputs:
      - id: catalog
        source: resize-collection/catalog
      - id: collection
        source: resize-collection/collection
    outputs:
      - id: urls
        type: string[]
        outputBinding:
          loadContents: true
          glob: urls.txt
          outputEval: $(self[0].contents.split('\n'))
      - id: ids
        type: string[]
        outputBinding:
          loadContents: true
          glob: ids.txt
          outputEval: $(self[0].contents.split('\n'))
```

### Configuration Yaml Documentation

| Configuration key           | Description                                                                                                                                                                                                                                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                        | Generate workflow with this ID.                                                                                                                                                                                                                                                                                      |
| `doc`                       | Workflow documentation string.                                                                                                                                                                                                                                                                                       |
| `label`                     | Short human readable label.                                                                                                                                                                                                                                                                                          |
| `inputs`                    | List of input definitions for the workflow. Values for these are provided by the user when executing.                                                                                                                                                                                                                |
| `inputs[n].id`              | Unique input ID, cannot be the same as ID of another input, output or step. Duplicates between step inputs and workflow inputs are allowed (as seen in the example above), as they are referenced e.g. by `<step id>/<step input id>`, but this is generally discouraged if avoidable as it can introduce confusion. |
| `inputs[n].label`           | Short human readable label.                                                                                                                                                                                                                                                                                          |
| `inputs[n].doc`             | Documentation string for this object.                                                                                                                                                                                                                                                                                |
| `inputs[n].type`            | Input type, one of [CWL types](https://www.commonwl.org/v1.2/Workflow.html#CWLType).                                                                                                                                                                                                                                 |
| `inputs[n].default`         | Default input value, if not provided by the user. Makes the input optional.                                                                                                                                                                                                                                          |
| `outputs`                   | List of outputs created by the workflow.                                                                                                                                                                                                                                                                             |
| `outputs[n].id`             | Unique output ID.                                                                                                                                                                                                                                                                                                    |
| `outputs[n].type`           | Output type, one of [CWL types](https://www.commonwl.org/v1.2/Workflow.html#CWLType).                                                                                                                                                                                                                                |
| `outputs[n].source`         | Source of the output data. In format `<step id>/<step output id>`.                                                                                                                                                                                                                                                   |
| `steps`                     | List of steps to be performed by the workflow.                                                                                                                                                                                                                                                                       |
| `steps[n].id`               | Unique ID within step object.                                                                                                                                                                                                                                                                                        |
| `steps[n].script`           | Path (relative to the repository root) to python script performing this step.                                                                                                                                                                                                                                        |
| `steps[n].requirements`     | Path (relative to the repository root) to a requirements.txt style file containing python dependencies for the script.                                                                                                                                                                                               |
| `steps[n].inputs`           | List of inputs required by the script                                                                                                                                                                                                                                                                                |
| `steps[n].inputs[m].id`     | Unique ID within the step, must match parameter name from the script cli. object.                                                                                                                                                                                                                                    |
| `steps[n].inputs[m].source` | Source of the input data. Steps can consume either workflow inputs or outputs from other steps (this creates dependency between steps). Format can be either `<workflow ID>/<wf input ID>` or `<step ID>/<step output ID>`                                                                                           |
| `steps[n].outputs`          | List of step outputs. cwl-gen cannot determine outputs from provided python scripts automatically. Provide valid [CWL CommandLineTool](https://www.commonwl.org/v1.2/CommandLineTool.html#CommandOutputParameter) outputs section here.                                                                              |

## Generator

### Using GitHub Actions

The recommended way to use this tool is through a GitHub reusable workflow which generates the application package, builds and pushes docker images to ghcr. See (workflow)[.github/workflows/generate-reusable.yml] to reference available inputs. Workflow needs certain write permissions as it's pushing the generated files to the repo and also pushing container images to the registry.

Example usage:

```yaml
name: Generate EOAP
on:
  push:
  workflow_dispatch:
jobs:
  build-push:
    uses: EO-DataHub/eoap-gen/.github/workflows/generate-reusable.yml@main
    with:
      config: eoap-gen-config.yml
    permissions:
      contents: write
      packages: write
      attestations: write
      id-token: write
```

There is also a GitHub composite action available in this repository to only execute eoap-gen. It will generate eoap, the rest is up to the user. See (action)[action.yml] to reference available inputs and default values.

Example usage:

```yaml
- name: Run eoap-gen
  id: gen
  uses: EO-DataHub/eoap-gen@main
  with:
    config: path/to/config.yml
    output: output-dir
```

### Running locally

#### Requirements

- [pipx](https://pipx.pypa.io/latest/installation/)

#### Running without installation:

```
pipx run --spec git+https://github.com/EO-DataHub/eoap-gen.git eoap-gen --help
```

#### Installing with pipx:

```
pipx install git+https://github.com/EO-DataHub/eoap-gen
eoap-gen --help
```

#### Example usage

```bash
eoap-gen generate \
  --config=eoap-gen-config.yml \
  --output=eoap-gen-out \
  --docker-url-base=ghcr.io/user/repo \
  --docker-tag=main
```

# Development

[Install poetry](https://python-poetry.org/docs/#installation)

Install package deps:

```
make install
```

Run QA checks:

```
make check
```
