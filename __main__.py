import pulumi

from cluster.node_pool import NodePoolManager
from cluster.oke import OKEClusterManager
from network.gateways import GatewayManager
from network.routing import RouteTableManager
from network.security import SecurityListManager
from network.subnets import SubnetManager
from network.vcn import VCNManager


def main():
    # Step 1: VCN 생성
    vcn_manager = VCNManager()
    vcn = vcn_manager.create_vcn()

    # Step 2: 게이트웨이 생성 (인터넷, NAT, 서비스)
    gateway_manager = GatewayManager(vcn)
    internet_gateway, nat_gateway, service_gateway = gateway_manager.create_all_gateways()

    # Step 3: 라우트 테이블 생성 (프라이빗, 퍼블릭)
    route_table_manager = RouteTableManager(vcn, internet_gateway, nat_gateway, service_gateway)
    route_table_private, route_table_public = route_table_manager.create_all_route_tables()

    # Step 4: 보안 리스트 생성 (노드, K8s API, 서비스 로드 밸런서)
    security_list_manager = SecurityListManager(vcn)
    node_security_list, k8s_api_security_list, service_lb_security_list = (
        security_list_manager.create_all_security_lists()
    )

    # Step 5: 서브넷 생성 (서비스 로드 밸런서, 노드, K8s API)
    subnet_manager = SubnetManager(
        vcn,
        route_table_private,
        route_table_public,
        node_security_list,
        k8s_api_security_list,
    )
    service_lb_subnet, node_subnet, k8s_api_subnet = subnet_manager.create_all_subnets()

    # Step 6: OKE 클러스터 생성
    oke_cluster_manager = OKEClusterManager(vcn, k8s_api_subnet, service_lb_subnet)
    oke_cluster = oke_cluster_manager.create_cluster()

    # Step 7: OKE 노드 풀 생성
    node_pool_manager = NodePoolManager(oke_cluster, node_subnet)
    node_pool = node_pool_manager.create_node_pool()

    # Step 8: Pulumi로 필요한 리소스 ID를 export
    pulumi.export('vcn_id', vcn.id)

    pulumi.export('internet_gateway_id', internet_gateway.id)
    pulumi.export('nat_gateway_id', nat_gateway.id)
    pulumi.export('service_gateway_id', service_gateway.id)

    pulumi.export('route_table_private_id', route_table_private.id)
    pulumi.export('route_table_public_id', route_table_public.id)

    pulumi.export('node_security_list_id', node_security_list.id)
    pulumi.export('k8s_api_security_list_id', k8s_api_security_list.id)
    pulumi.export('service_lb_security_list_id', service_lb_security_list.id)

    pulumi.export('service_lb_subnet_id', service_lb_subnet.id)
    pulumi.export('node_subnet_id', node_subnet.id)
    pulumi.export('k8s_api_subnet_id', k8s_api_subnet.id)
    pulumi.export('oke_cluster_id', oke_cluster.id)
    pulumi.export('node_pool_id', node_pool.id)


if __name__ == '__main__':
    main()
