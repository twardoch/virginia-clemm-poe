#!/usr/bin/env bash
./src_docs/update_docs.py
llms . "*.txt,docs"
uvx hatch clean
gitnextver .
uvx hatch build
uvx hatch publish
