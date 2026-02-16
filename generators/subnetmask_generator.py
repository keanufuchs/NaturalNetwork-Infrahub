import ipaddress
from infrahub_sdk.generator import InfrahubGenerator


class SubnetmaskGenerator(InfrahubGenerator):

    async def generate(self, data: dict) -> None:

        for ip_address in self.nodes:

            cidr = ip_address.address.value
            ipif = ipaddress.ip_interface(cidr)
            ip_address.subnetmask.value = str(ipif.network.netmask)
            await ip_address.save()
