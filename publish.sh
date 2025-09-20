#!/usr/bin/env bash
uv pip install --system --upgrade -e .
python -m virginia_clemm_poe update --all --force --verbose
python ./src_docs/update_docs.py
llms . "*.txt,docs"
uvx hatch clean
gitnextver .
uvx hatch build
uv publish
say "Virginia Clemm Poe is ready!"
