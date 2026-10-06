# CodeableModels

CodeableModels is a Python library for programmatically creating software design models
akin to UML, built on a lightweight and radically simplified meta-model. It lets you define
metaclasses, classes, objects, stereotypes, associations, and their relationships entirely
in code — with no external dependencies at runtime.

## Features

- **Metaclasses and classes** — define your domain meta-model and instantiate it with classes
- **Objects** — instances of classes with typed attribute values
- **Stereotypes** — UML-style stereotype extensions with tagged values
- **Associations and links** — directed/undirected associations, role names, multiplicities, link objects
- **Inheritance** — single and multiple inheritance for metaclasses, classes, and stereotypes
- **Bundles, packages, layers** — group and organize model elements
- **Enumerations** — typed enum attributes
- **PlantUML rendering** — generate class and object diagrams via the bundled `plant_uml_renderer` module
- **Zero runtime dependencies** — the core library uses only the Python standard library

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) for managing the environment and dependencies

Create the virtual environment and install the development/testing and documentation dependencies:

```bash
uv sync
```

## Installation

CodeableModels is used as a source import — clone the repository and add it to your Python path:

```bash
git clone https://github.com/uzdun/CodeableModels.git
```

Then import directly:

```python
from codeable_models import CMetaclass, CClass, CObject, CAttribute, CException, CEnum, CStereotype
```

## Quick Start

```python
from codeable_models import CMetaclass, CClass, CObject, CAttribute, CStereotype, CEnum

# Define a metaclass (the "type of a class")
entity = CMetaclass("Entity", attributes={"name": ""})

# Define a class that conforms to the metaclass; metaclass attributes
# (here "name") are set as values on the class, not on its objects
person = CClass(entity, "Person", values={"name": "Person"},
                attributes={"name": "", "age": 0})

# Instantiate an object (it can only use attributes defined on its class)
alice = CObject(person, "Alice", values={"name": "Alice", "age": 30})
print(alice.get_value("name"))  # "Alice"

# Define an association
address = CClass(entity, "Address", attributes={"street": "", "city": ""})
person.association(address, "lives at: [resident] * -> [address] 1")

# Stereotypes
persistent = CStereotype("Persistent", attributes={"table": ""})
entity.stereotypes = persistent
person.stereotype_instances = persistent
person.set_tagged_value("table", "persons", persistent)
```

## Running the Tests

```bash
uv run pytest
```

Run with verbose output:

```bash
uv run pytest -v
```

## Building the Documentation

Documentation is built with Sphinx. The docs dependencies are installed by `uv sync`.
Build from the `docsrc/` directory:

```bash
cd docsrc
uv run make html        # build HTML docs into docsrc/build/html/
uv run make docs        # copy build into the top-level docs/ folder
```

The latest built documentation is available at:
[https://uzdun.github.io/CodeableModels/](https://uzdun.github.io/CodeableModels/)

## PlantUML Rendering

The `plant_uml_renderer` module generates PlantUML diagrams from your models.
It requires the external `plantuml.jar` to be available. Download it from
[https://plantuml.com/download](https://plantuml.com/download) and configure the path
in `plant_uml_renderer/plant_uml_generator.py`.

```python
from plant_uml_renderer import PlantUMLGenerator
```

See the `samples/` directory for usage examples.

## Project Structure

```
codeable_models/          Core modeling API (zero external dependencies)
  internal/               Internal utilities (commons, stereotype_holders, var_values)
tests/                    Test suite (35 test files, ~820 tests) — run with uv run pytest
metamodels/               Example domain metamodels (activity, component, deployment, etc.)
plant_uml_renderer/       PlantUML class/object diagram renderer
samples/                  Usage examples with rendered diagrams
docsrc/                   Sphinx documentation source
docs/                     Built documentation (served via GitHub Pages)
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the code of conduct and
the process for submitting pull requests.

## Versioning

This project uses [SemVer](https://semver.org/) for versioning. See the
[tags on this repository](https://github.com/uzdun/CodeableModels/tags) for available versions.

## Authors

- **Uwe Zdun** — initial work — [https://github.com/uzdun/](https://github.com/uzdun/)

## License

Apache 2.0 — see the [LICENSE](LICENSE) file for details.
