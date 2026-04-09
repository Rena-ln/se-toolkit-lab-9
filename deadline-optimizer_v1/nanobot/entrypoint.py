#!/usr/bin/env python3
"""Nanobot entrypoint that resolves environment variables into config.json."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def resolve_env_vars(config_path: Path, output_path: Path) -> dict:
    """Read config.json and resolve environment variable placeholders."""
    with open(config_path) as f:
        config = json.load(f)

    config_str = json.dumps(config)

    # Pattern: ${VAR_NAME:-default} or ${VAR_NAME}
    pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'

    def replacer(match):
        var_name = match.group(1)
        default = match.group(2) or ""
        return os.getenv(var_name, default)

    resolved_str = re.sub(pattern, replacer, config_str)
    resolved_config = json.loads(resolved_str)

    with open(output_path, 'w') as f:
        json.dump(resolved_config, f, indent=2)

    return resolved_config


def main():
    """Resolve config and start nanobot gateway."""
    config_path = Path(__file__).parent / "config.json"
    output_path = Path(__file__).parent / "config.resolved.json"

    print("Resolving environment variables into config...")
    config = resolve_env_vars(config_path, output_path)
    print(f"Config resolved. Agent: {config['agent']['name']}")

    # Start nanobot gateway
    cmd = ["nanobot", "gateway", "--config", str(output_path)]
    print(f"Starting: {' '.join(cmd)}")

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
