class: Workflow
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
cwlVersion: v1.0
steps:
- id: get_urls
  in:
  - id: catalog
    source: resize-collection/catalog
  - id: collection
    source: resize-collection/collection
  out:
  - id: urls
  - id: ids
  run: /home/figi/software/work/eodh/eoap-gen/tests/output/cli/get_urls/get_urls.cwl
- id: process
  in:
  - id: outsize_x
    source: resize-collection/outsize_x
  - id: outsize_y
    source: resize-collection/outsize_y
  - id: url
    source: get_urls/urls
  - id: id
    source: get_urls/ids
    valueFrom: $(self + "_resized.tif")
  out:
  - id: resized
  run: /home/figi/software/work/eodh/eoap-gen/tests/output/cli/process/process.cwl
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
  run: /home/figi/software/work/eodh/eoap-gen/tests/output/cli/make_stac/make_stac.cwl
