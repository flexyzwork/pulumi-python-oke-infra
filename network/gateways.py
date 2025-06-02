import pulumi_oci as oci

import config as cfg


class GatewayManager:
    def __init__(self, vcn):
        self.vcn = vcn
        self.internet_gateway = None
        self.nat_gateway = None
        self.service_gateway = None

    def create_internet_gateway(self):
        """인터넷 게이트웨이 생성 및 할당"""
        return oci.core.InternetGateway(
            'internetGateway',
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=cfg.INTERNET_GATEWAY_DISPLAY_NAME,
            enabled=True,
            vcn_id=self.vcn.id,
        )

    def create_nat_gateway(self):
        """NAT 게이트웨이 생성 및 할당"""
        return oci.core.NatGateway(
            'natGateway',
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=cfg.NAT_GATEWAY_DISPLAY_NAME,
            vcn_id=self.vcn.id,
        )

    def create_service_gateway(self):
        """서비스 게이트웨이 생성 및 할당"""
        return oci.core.ServiceGateway(
            'serviceGateway',
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=cfg.SERVICE_GATEWAY_DISPLAY_NAME,
            services=[oci.core.ServiceGatewayServiceArgs(service_id=cfg.SERVICE_ID)],
            vcn_id=self.vcn.id,
        )

    def create_all_gateways(self):
        """모든 게이트웨이 생성 및 반환"""
        self.internet_gateway = self.create_internet_gateway()
        self.nat_gateway = self.create_nat_gateway()
        self.service_gateway = self.create_service_gateway()
        return self.internet_gateway, self.nat_gateway, self.service_gateway
