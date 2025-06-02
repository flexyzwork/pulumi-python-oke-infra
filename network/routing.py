import pulumi_oci as oci

import config as cfg


class RouteTableManager:
    """
    라우트 테이블 생성 및 관리 클래스
    """

    def __init__(self, vcn, internet_gateway, nat_gateway, service_gateway):
        self.vcn = vcn
        self.internet_gateway = internet_gateway
        self.nat_gateway = nat_gateway
        self.service_gateway = service_gateway
        self.route_table_private = None
        self.route_table_public = None

    def _create_route_table(self, display_name, route_rules):
        """
        라우트 테이블을 생성하는 공통 메소드
        """
        return oci.core.RouteTable(
            display_name,
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=display_name,
            route_rules=route_rules,
            vcn_id=self.vcn.id,
        )

    def create_route_table_private(self, nat_gateway, service_gateway):
        """
        프라이빗 라우트 테이블 생성 메소드
        """
        route_rules = [
            oci.core.RouteTableRouteRuleArgs(
                description='인터넷으로의 트래픽',
                destination='0.0.0.0/0',
                destination_type='CIDR_BLOCK',
                network_entity_id=nat_gateway.id,
            ),
            oci.core.RouteTableRouteRuleArgs(
                description='OCI 서비스로의 트래픽',
                destination=cfg.SERVICE_CIDR,
                destination_type='SERVICE_CIDR_BLOCK',
                network_entity_id=service_gateway.id,
            ),
        ]
        return self._create_route_table('oke-route-table-private', route_rules)

    def create_route_table_public(self, internet_gateway):
        """
        퍼블릭 라우트 테이블 생성 메소드
        """
        route_rules = [
            oci.core.RouteTableRouteRuleArgs(
                description='퍼블릭 인터넷 트래픽',
                destination='0.0.0.0/0',
                destination_type='CIDR_BLOCK',
                network_entity_id=internet_gateway.id,
            )
        ]
        return self._create_route_table('oke-route-table-public', route_rules)

    def create_all_route_tables(self):
        """
        모든 라우트 테이블을 생성하는 메소드
        """
        self.route_table_private = self.create_route_table_private(self.nat_gateway, self.service_gateway)
        self.route_table_public = self.create_route_table_public(self.internet_gateway)
        return self.route_table_private, self.route_table_public
