$graph:
- class: CommandLineTool
  id: get_urls
  inputs:
  - id: catalog
    inputBinding:
      prefix: --catalog
    type:
    - 'null'
    - string
  - id: collection
    inputBinding:
      prefix: --collection
    type:
    - 'null'
    - string
  requirements:
  - class: DockerRequirement
    dockerPull: ghcr.io/figi44/eoap/get_urls:main
  - class: InlineJavascriptRequirement
  doc: "None\n"
  baseCommand:
  - /usr/local/bin/_entrypoint.sh
  - env
  - HOME=/tmp
  - python
  - /app/app.py
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
- class: CommandLineTool
  id: make_stac
  inputs:
  - id: files
    doc: FILES
    type:
      type: array
      items: File
  outputs:
  - id: stac_catalog
    outputBinding:
      glob: .
    type: Directory
  requirements:
  - class: DockerRequirement
    dockerPull: ghcr.io/figi44/eoap/make_stac:main
  - class: InlineJavascriptRequirement
  doc: "None\n"
  baseCommand:
  - python
  - /app/app.py
- class: CommandLineTool
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
  - type: File
    outputBinding:
      glob: '*.tif'
    id: resized
  requirements:
  - class: DockerRequirement
    dockerPull: ghcr.io/osgeo/gdal:ubuntu-small-latest
  - class: InlineJavascriptRequirement
  baseCommand: gdal_translate
  id: process
- class: Workflow
  id: resize-collection
  inputs:
  - id: catalog
    label: catalog
    doc: full catalog path
    default: supported-datasets/ceda-stac-fastapi
    type: string
  - id: collection
    label: collection id
    doc: collection id
    default: sentinel2_ard
    type: string
  - id: outsize_x
    label: outsize_x
    doc: outsize_x
    default: 5%
    type: string
  - id: outsize_y
    label: outsize_y
    doc: outsize_y
    default: 5%
    type: string
  outputs:
  - id: stac_output
    outputSource:
    - make_stac/stac_catalog
    type: Directory
  requirements:
  - class: ScatterFeatureRequirement
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 1024
  label: Resize collection cogs
  doc: Resize collection cogs
  steps:
  - id: get_urls
    in:
    - id: catalog
      source: catalog
    - id: collection
      source: collection
    out:
    - id: urls
    - id: ids
    run: '#get_urls'
  - id: process
    in:
    - id: outsize_x
      source: outsize_x
    - id: outsize_y
      source: outsize_y
    - id: url
      source: get_urls/urls
    - id: id
      source: get_urls/ids
      valueFrom: $(self + "_resized.tif")
    out:
    - id: resized
    run: '#process'
    scatter:
    - url
    - id
    scatterMethod: dotproduct
  - id: make_stac
    in:
    - id: files
      source: process/resized
    out:
    - id: stac_catalog
    run: '#make_stac'
cwlVersion: v1.0
