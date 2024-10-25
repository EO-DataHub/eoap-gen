class: CommandLineTool
id: 
  file:///home/figi/software/projects/eodh/eoap-gen/tests/data/ref-out/cli/make_stac/make_stac.cwl
inputs:
- id: files
  doc: FILES
  type: File[]
outputs:
- id: stac_catalog
  outputBinding:
    glob: .
  type: Directory
hints:
- class: DockerRequirement
  dockerPull: ghcr.io/figi44/eoap/make_stac:main
- class: InlineJavascriptRequirement
doc: |
  None
cwlVersion: v1.0
baseCommand:
- python
- /app/app.py
