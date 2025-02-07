$graph:
- class: CommandLineTool
  id: '#get_urls'
  inputs:
  - id: '#get_urls/catalog'
    inputBinding:
      prefix: --catalog
    type:
    - 'null'
    - string
  - id: '#get_urls/collection'
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
  - id: '#get_urls/ids'
    outputBinding:
      glob: ids.txt
      loadContents: true
      outputEval: $(self[0].contents.split('\n'))
    type:
      items: string
      type: array
  - id: '#get_urls/urls'
    outputBinding:
      glob: urls.txt
      loadContents: true
      outputEval: $(self[0].contents.split('\n'))
    type:
      items: string
      type: array
- class: CommandLineTool
  id: '#make_stac'
  inputs:
  - id: '#make_stac/files'
    doc: FILES
    type:
      type: array
      items: File
  outputs:
  - id: '#make_stac/stac_catalog'
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
  - id: '#process/url'
    inputBinding:
      position: 1
      prefix: /vsicurl/
      separate: false
    type: string
  - id: '#process/id'
    inputBinding:
      position: 2
      separate: false
      valueFrom: $(self + "_resized.tif")
    type: string
  - id: '#process/outsize_x'
    inputBinding:
      position: 4
      prefix: -outsize
      separate: true
    type: string
  - id: '#process/outsize_y'
    inputBinding:
      position: 5
      separate: false
    type: string
  outputs:
  - type: File
    outputBinding:
      glob: '*.tif'
    id: '#process/resized'
  requirements:
  - class: DockerRequirement
    dockerPull: ghcr.io/osgeo/gdal:ubuntu-small-latest
  - class: InlineJavascriptRequirement
  baseCommand: gdal_translate
  id: '#process'
- class: Workflow
  id: '#resize-collection'
  inputs:
  - id: '#resize-collection/catalog'
    label: catalog
    doc: full catalog path
    default: supported-datasets/ceda-stac-fastapi
    type: string
  - id: '#resize-collection/collection'
    label: collection id
    doc: collection id
    default: sentinel2_ard
    type: string
  - id: '#resize-collection/outsize_x'
    label: outsize_x
    doc: outsize_x
    default: 5%
    type: string
  - id: '#resize-collection/outsize_y'
    label: outsize_y
    doc: outsize_y
    default: 5%
    type: string
  outputs:
  - id: '#resize-collection/stac_output'
    outputSource:
    - '#resize-collection/make_stac/stac_catalog'
    type: Directory
  requirements:
  - class: ScatterFeatureRequirement
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 1024
  label: Resize collection cogs
  doc: Resize collection cogs
  steps:
  - id: '#resize-collection/get_urls'
    in:
    - id: '#resize-collection/get_urls/catalog'
      source: '#resize-collection/catalog'
    - id: '#resize-collection/get_urls/collection'
      source: '#resize-collection/collection'
    out:
    - id: '#resize-collection/get_urls/urls'
    - id: '#resize-collection/get_urls/ids'
    run: '#get_urls'
  - id: '#resize-collection/process'
    in:
    - id: '#resize-collection/process/outsize_x'
      source: '#resize-collection/outsize_x'
    - id: '#resize-collection/process/outsize_y'
      source: '#resize-collection/outsize_y'
    - id: '#resize-collection/process/url'
      source: '#resize-collection/get_urls/urls'
    - id: '#resize-collection/process/id'
      source: '#resize-collection/get_urls/ids'
      valueFrom: $(self + "_resized.tif")
    out:
    - id: '#resize-collection/process/resized'
    run: '#process'
    scatter:
    - '#resize-collection/process/url'
    - '#resize-collection/process/id'
    scatterMethod: dotproduct
  - id: '#resize-collection/make_stac'
    in:
    - id: '#resize-collection/make_stac/files'
      source: '#resize-collection/process/resized'
    out:
    - id: '#resize-collection/make_stac/stac_catalog'
    run: '#make_stac'
cwlVersion: v1.0
