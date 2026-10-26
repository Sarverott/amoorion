from amoorion.cli import main

# Only when run (python -m); importing it, as the API reference does, starts nothing.
if __name__ == "__main__":
    raise SystemExit(main(["mcp"]))
