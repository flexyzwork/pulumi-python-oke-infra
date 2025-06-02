import pulumi_oci as oci

import config as cfg


class SubnetManager:
    """
    서브넷 생성 및 관리 클래스
    """

    def __init__(
        self,
        vcn,
        route_table_private,
        route_table_public,
        node_security_list,
        k8s_api_security_list,
    ):
        self.vcn = vcn
        self.route_table_private = route_table_private
        self.route_table_public = route_table_public
        self.node_security_list = node_security_list
        self.k8s_api_security_list = k8s_api_security_list
        self.service_lb_subnet = None
        self.node_subnet = None
        self.k8s_api_subnet = None

    def create_subnet(
        self,
        cidr_block,
        display_name,
        dns_label,
        route_table,
        prohibit_public_ip_on_vnic,
        security_lists,
    ):
        """
        서브넷 생성 메소드
        """
        subnet = oci.core.Subnet(
            f'{display_name}-subnet',
            cidr_block=cidr_block,
            compartment_id=cfg.COMPARTMENT_ID,
            display_name=display_name,
            dns_label=dns_label,
            prohibit_public_ip_on_vnic=prohibit_public_ip_on_vnic,
            route_table_id=route_table.id,
            security_list_ids=[sl.id for sl in security_lists],
            vcn_id=self.vcn.id,
        )
        return subnet

    def create_all_subnets(self):
        """
        모든 서브넷을 생성하는 메소드
        """
        self.service_lb_subnet = self.create_subnet(
            cfg.SERVICE_LB_SUBNET_CIDR_BLOCK,
            'oke-svc',
            'lbsub',
            self.route_table_private,
            False,
            [self.node_security_list],
        )
        self.node_subnet = self.create_subnet(
            cfg.NODE_SUBNET_CIDR_BLOCK,
            'oke-node',
            'nodesub',
            self.route_table_private,
            True,
            [self.node_security_list],
        )
        self.k8s_api_subnet = self.create_subnet(
            cfg.K8S_API_SUBNET_CIDR_BLOCK,
            'oke-api',
            'apisub',
            self.route_table_public,
            False,
            [self.node_security_list, self.k8s_api_security_list],
        )
        return self.service_lb_subnet, self.node_subnet, self.k8s_api_subnet
