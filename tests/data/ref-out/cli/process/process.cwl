class: CommandLineTool
inputs:
- id: url
  inputBinding:
    position: 1
    prefix: /vsicurl/
    separate: false
  type: string
- id: id
  inputBinding:
    position: 2
    separate: false
    valueFrom: $(self + "_resized.tif")
  type: string
- id: outsize_x
  inputBinding:
    position: 4
    prefix: -outsize
    separate: true
  type: string
- id: outsize_y
  inputBinding:
    position: 5
    separate: false
  type: string
outputs:
  resized:
    type: File
    outputBinding:
      glob: '*.tif'
requirements:
- class: DockerRequirement
  dockerPull: ghcr.io/osgeo/gdal:ubuntu-small-latest
- class: InlineJavascriptRequirement
cwlVersion: v1.0
baseCommand: gdal_translate
