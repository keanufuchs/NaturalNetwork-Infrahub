from infrahub_sdk.transforms import InfrahubTransform


class SwitchHostnameTransform(InfrahubTransform):
    query = "dcim_switch_names"

    async def transform(self, data):
        nodes = self.nodes
        for node in nodes:
            print(node.name.value)
        # return nodes