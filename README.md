# EOAP-GEN

A CLI tool for generating Earth Observation Application Packages including CWL workflows and Dockerfiles.

# Usage

### Requirements

- [pipx](https://pipx.pypa.io/latest/installation/)

### Running without installation

```
pipx run git+https://github.com/... --help
```

### Installation

pipx will make the `eoap-gen` command available locally.

```
pipx install git+https://github.com/....
eoap-gen --help
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
