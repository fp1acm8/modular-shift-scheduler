# Minimal Example

This directory hosts a reproducible Excel workbook that demonstrates the CLI. The binary file is not
checked into the repository; generate it with the helper script:

```bash
python examples/minimal/generate_config.py
```

Then run the solver from the project root (after installing the package):

```bash
python -m pip install -e .
modular-shift-scheduler examples/minimal/config.xlsx
```

The command prints a JSON object describing the solver status, assignment matrix and any shortages.
