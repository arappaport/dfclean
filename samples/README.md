# dfclean-demo

Minimal Poetry project demonstrating `arappaport/dfclean`.

## Setup

```bash
poetry install
```

## Run

```bash
poetry run python run_dfclean.py
```

Or with a custom CSV:
```bash
cp /your/path/data_cleaned_expected.csv .
poetry run python -m dfclean_demo.main
```

## Notes

- `dfclean` is installed directly from GitHub (not on PyPI under this name).
- `dfclean.clean()` is not in the exported public API; this project uses
  `clean()` which is the documented entrypoint for the clean(). See `dfclean_demo/run_dfclean.py`.
