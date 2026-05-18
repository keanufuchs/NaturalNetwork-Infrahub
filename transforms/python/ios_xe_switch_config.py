from jinja2 import Environment, FileSystemLoader

from infrahub_sdk.transforms import InfrahubTransform


class IosXeSwitchConfigTransform(InfrahubTransform):
    query = "dcim_switch_ios_xe_config"

    async def transform(self, data: dict) -> str:
        edges = data["DcimSwitch"]["edges"]
        if not edges:
            return "! No switch found\n"

        switch = edges[0]["node"]
        vlans = self._collect_vlans(switch)

        template_dir = f"{self.root_directory}/transforms/jinja"
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("ios_xe_switch_config.j2")
        return template.render(switch=switch, vlans=vlans)

    def _collect_vlans(self, switch: dict) -> list[dict]:
        vlan_map: dict[int, str] = {}

        for edge in switch["interfaces"]["edges"]:
            iface = edge["node"]
            if iface["untagged_vlan"]["node"]:
                v = iface["untagged_vlan"]["node"]
                vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]
            for tv_edge in iface["tagged_vlans"]["edges"]:
                v = tv_edge["node"]
                vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]

        for edge in switch["svi_interfaces"]["edges"]:
            svi = edge["node"]
            if svi["vlan"]["node"]:
                v = svi["vlan"]["node"]
                vlan_map[v["vlan_id"]["value"]] = v["name"]["value"]

        return [{"vlan_id": vid, "name": name} for vid, name in sorted(vlan_map.items())]
