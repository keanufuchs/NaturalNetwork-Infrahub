from infrahub_sdk.transforms import InfrahubTransform


class SwitchHostnameTransform(InfrahubTransform):
    query = "dcim_switch_names"

    async def transform(self, data):
        switch = self.nodes[0]
        switch_name = switch.name.value
        return (
            f"hostname {switch_name}",
        )
