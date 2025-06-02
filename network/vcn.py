import pulumi_oci as oci

import config as cfg


class VCNManager:
    def __init__(self):
        self.vcn = None

    def create_vcn(self):
        self.vpn = oci.core.Vcn(
            'vcn',
            cidr_block=cfg.VCN_CIDR_BLOCK,
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=cfg.VCN_DISPLAY_NAME,
            dns_label='mgmt',
        )
        return self.vpn
