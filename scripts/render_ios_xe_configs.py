#!/usr/bin/env python3
"""Render IOS-XE switch configs from InfraHub SoT.

Usage:
    uv run python scripts/render_ios_xe_configs.py
    INFRAHUB_SITE=Koeln uv run python scripts/render_ios_xe_configs.py

Environment:
    INFRAHUB_ADDRESS  InfraHub server URL (default: http://localhost:8000)
    INFRAHUB_BRANCH   InfraHub branch to query (default: main)
    INFRAHUB_SITE     Site name to filter switches by (default: Bonn)

Output: generated/configs/<switch-name>.cfg
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

INFRAHUB_ADDRESS = os.getenv("INFRAHUB_ADDRESS", "http://localhost:8000")
INFRAHUB_BRANCH = os.getenv("INFRAHUB_BRANCH", "main")
INFRAHUB_SITE = os.getenv("INFRAHUB_SITE", "Bonn")

REPO_DIR = Path(__file__).parent.parent
QUERY_FILE = REPO_DIR / "queries" / "dcim_switch_full_config.gql"
TEMPLATE_DIR = REPO_DIR / "transforms" / "jinja"
OUTPUT_DIR = REPO_DIR / "generated" / "configs"


def query_infrahub(query: str, variables: dict) -> dict:
    url = f"{INFRAHUB_ADDRESS}/graphql/{INFRAHUB_BRANCH}"
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def collect_vlans(switch_node: dict) -> list[dict]:
    """Return sorted list of unique VLANs used by a switch."""
    vlan_map: dict[int, str] = {}

    for edge in switch_node["interfaces"]["edges"]:
        iface = edge["node"]
        if iface["untagged_vlan"]["node"]:
            v = iface["untagged_vlan"]["node"]
            vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]
        for tv_edge in iface["tagged_vlans"]["edges"]:
            v = tv_edge["node"]
            vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]

    for edge in switch_node["svi_interfaces"]["edges"]:
        svi = edge["node"]
        if svi["vlan"]["node"]:
            v = svi["vlan"]["node"]
            vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]

    return [{"vlan_id": vid, "name": name} for vid, name in sorted(vlan_map.items())]


def main() -> None:
    query = QUERY_FILE.read_text()
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("ios_xe_switch_config.j2")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Querying InfraHub ({INFRAHUB_ADDRESS}, branch={INFRAHUB_BRANCH}, site={INFRAHUB_SITE})")
    result = query_infrahub(query, {"site": INFRAHUB_SITE})

    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
        sys.exit(1)

    switches = result["data"]["DcimSwitch"]["edges"]
    print(f"Found {len(switches)} switches")

    for edge in switches:
        node = edge["node"]
        switch_name = node["name"]["value"]
        vlans = collect_vlans(node)
        rendered = template.render(switch=node, vlans=vlans)
        out_path = OUTPUT_DIR / f"{switch_name}.cfg"
        out_path.write_text(rendered)
        print(f"  {out_path.relative_to(REPO_DIR)}")

    print(f"Done. {len(switches)} configs written to {OUTPUT_DIR.relative_to(REPO_DIR)}/")


if __name__ == "__main__":
    main()
