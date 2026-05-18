#!/usr/bin/env python3
"""Generate IOS-XE switch configs via InfraHub transform API.

Usage:
    uv run python scripts/render_ios_xe_configs.py
    INFRAHUB_SITE=Koeln uv run python scripts/render_ios_xe_configs.py
    INFRAHUB_OUTPUT_DIR=../naturalnetwork-cml-terraform/generated/configs \
        uv run python scripts/render_ios_xe_configs.py

Environment:
    INFRAHUB_ADDRESS    InfraHub server URL (default: http://localhost:8000)
    INFRAHUB_BRANCH     InfraHub branch to query (default: main)
    INFRAHUB_SITE       Location name filter (default: Bonn)
    INFRAHUB_OUTPUT_DIR Output directory for .cfg files
                        (default: <repo>/generated/configs)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

INFRAHUB_ADDRESS = os.getenv("INFRAHUB_ADDRESS", "http://localhost:8000").rstrip("/")
INFRAHUB_BRANCH = os.getenv("INFRAHUB_BRANCH", "main")
INFRAHUB_SITE = os.getenv("INFRAHUB_SITE", "")

REPO_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(os.getenv("INFRAHUB_OUTPUT_DIR", str(REPO_DIR / "generated" / "configs")))

_SWITCH_NAMES_QUERY_ALL = """
query {
  DcimSwitch {
    edges {
      node {
        name { value }
      }
    }
  }
}
"""

_SWITCH_NAMES_QUERY_SITE = """
query ($site: String) {
  DcimSwitch(location__name__value: $site) {
    edges {
      node {
        name { value }
      }
    }
  }
}
"""


def _graphql(query: str, variables: dict) -> dict:
    url = f"{INFRAHUB_ADDRESS}/graphql/{INFRAHUB_BRANCH}"
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _fetch_transform(switch_name: str) -> str:
    params = urllib.parse.urlencode({"name": switch_name, "branch": INFRAHUB_BRANCH})
    url = f"{INFRAHUB_ADDRESS}/api/transform/python/ios_xe_switch_config?{params}"
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    site_info = f"site={INFRAHUB_SITE}" if INFRAHUB_SITE else "all sites"
    print(f"InfraHub: {INFRAHUB_ADDRESS} | branch={INFRAHUB_BRANCH} | {site_info}")
    print(f"Output:   {OUTPUT_DIR}")

    if INFRAHUB_SITE:
        result = _graphql(_SWITCH_NAMES_QUERY_SITE, {"site": INFRAHUB_SITE})
    else:
        result = _graphql(_SWITCH_NAMES_QUERY_ALL, {})
    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        sys.exit(1)

    switches = [e["node"]["name"]["value"] for e in result["data"]["DcimSwitch"]["edges"]]
    if not switches:
        print("No switches found", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(switches)} switches: {', '.join(switches)}\n")

    for name in switches:
        config = _fetch_transform(name)
        out_path = OUTPUT_DIR / f"{name}.cfg"
        out_path.write_text(config)
        print(f"  wrote {out_path}")

    print(f"\nDone. {len(switches)} configs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
