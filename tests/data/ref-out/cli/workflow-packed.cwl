$graph:
- class: CommandLineTool
  id: '#get_urls.cwl'
  inputs:
  - id: '#get_urls.cwl/catalog'
    inputBinding:
      prefix: --catalog
    type:
    - 'null'
    - string
  - id: '#get_urls.cwl/collection'
    inputBinding:
      prefix: --collection
    type:
    - 'null'
    - string
  hints:
  - class: DockerRequirement
    dockerPull: ghcr.io/figi44/eoap/get_urls:main
  - class: InlineJavascriptRequirement
  doc: "None\n"
  baseCommand:
  - python
  - /app/app.py
  outputs:
  - id: '#get_urls.cwl/ids'
    outputBinding:
      glob: ids.txt
      loadContents: true
      outputEval: $(self[0].contents.split('\n'))
    type:
      items: string
      type: array
  - id: '#get_urls.cwl/urls'
    outputBinding:
      glob: urls.txt
      loadContents: true
      outputEval: $(self[0].contents.split('\n'))
    type:
      items: string
      type: array
- class: CommandLineTool
  id: '#make_stac.cwl'
  inputs:
  - id: '#make_stac.cwl/files'
    doc: FILES
    type:
      type: array
      items: File
  outputs:
  - id: '#make_stac.cwl/stac_catalog'
    outputBinding:
      glob: .
    type: Directory
  hints:
  - class: DockerRequirement
    dockerPull: ghcr.io/figi44/eoap/make_stac:main
  - class: InlineJavascriptRequirement
  doc: "None\n"
  baseCommand:
  - python
  - /app/app.py
- class: CommandLineTool
  inputs:
  - id: '#process.cwl/url'
    inputBinding:
      position: 1
      prefix: /vsicurl/
      separate: false
    type: string
  - id: '#process.cwl/id'
    inputBinding:
      position: 2
      separate: false
      valueFrom: $(self + "_resized.tif")
    type: string
  - id: '#process.cwl/outsize_x'
    inputBinding:
      position: 4
      prefix: -outsize
      separate: true
    type: string
  - id: '#process.cwl/outsize_y'
    inputBinding:
      position: 5
      separate: false
    type: string
  outputs:
  - type: File
    outputBinding:
      glob: '*.tif'
    id: '#process.cwl/resized'
  hints:
  - class: DockerRequirement
    dockerPull: ghcr.io/osgeo/gdal:ubuntu-small-latest
  - class: InlineJavascriptRequirement
  baseCommand: gdal_translate
  id: '#process.cwl'
- class: Workflow
  id: '#main'
  inputs:
  - id: '#main/catalog'
    label: catalog
    doc: full catalog path
    default: supported-datasets/ceda-stac-fastapi
    type: string
  - id: '#main/collection'
    label: collection id
    doc: collection id
    default: sentinel2_ard
    type: string
  - id: '#main/outsize_x'
    label: outsize_x
    doc: outsize_x
    default: 5%
    type: string
  - id: '#main/outsize_y'
    label: outsize_y
    doc: outsize_y
    default: 5%
    type: string
  outputs:
  - id: '#main/stac_output'
    outputSource:
    - '#main/make_stac/stac_catalog'
    type: Directory
  requirements:
  - class: ScatterFeatureRequirement
  label: Resize collection cogs
  doc: Resize collection cogs
  steps:
  - id: '#main/get_urls'
    in:
    - id: '#main/get_urls/catalog'
      source: '#main/catalog'
    - id: '#main/get_urls/collection'
      source: '#main/collection'
    out:
    - id: '#main/get_urls/urls'
    - id: '#main/get_urls/ids'
    run: '#get_urls.cwl'
  - id: '#main/process'
    in:
    - id: '#main/process/outsize_x'
      source: '#main/outsize_x'
    - id: '#main/process/outsize_y'
      source: '#main/outsize_y'
    - id: '#main/process/url'
      source: '#main/get_urls/urls'
    - id: '#main/process/id'
      source: '#main/get_urls/ids'
      valueFrom: $(self + "_resized.tif")
    out:
    - id: '#main/process/resized'
    run: '#process.cwl'
    scatter:
    - '#main/process/url'
    - '#main/process/id'
    scatterMethod: dotproduct
  - id: '#main/make_stac'
    in:
    - id: '#main/make_stac/files'
      source: '#main/process/resized'
    out:
    - id: '#main/make_stac/stac_catalog'
    run: '#make_stac.cwl'
cwlVersion: v1.0
