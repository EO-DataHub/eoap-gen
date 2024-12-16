class: CommandLineTool
id: 
  file:///home/figi/software/work/eodh/eoap-gen/tests/output/cli/get_urls/get_urls.cwl
inputs:
- id: catalog
  inputBinding:
    prefix: --catalog
  type:
  - "null"
  - string
- id: collection
  inputBinding:
    prefix: --collection
  type:
  - "null"
  - string
outputs:
- id: ids
  outputBinding:
    glob: ids.txt
    loadContents: true
    outputEval: $(self[0].contents.split('\n'))
  type:
    items: string
    type: array
- id: urls
  outputBinding:
    glob: urls.txt
    loadContents: true
    outputEval: $(self[0].contents.split('\n'))
  type:
    items: string
    type: array
requirements:
- class: DockerRequirement
  dockerPull: ghcr.io/figi44/eoap/get_urls:main
- class: InlineJavascriptRequirement
doc: |
  None
cwlVersion: v1.0
baseCommand:
- /usr/local/bin/_entrypoint.sh
- python
- /app/app.py
