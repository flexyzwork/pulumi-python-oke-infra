import pulumi_oci as oci

import config as cfg


class SecurityListManager:
    """
    보안 리스트 생성 및 관리 클래스
    """

    def __init__(self, vcn):
        self.vcn = vcn
        self.node_security_list = None
        self.k8s_api_security_list = None
        self.service_lb_security_list = None

    def create_security_list(self, name, ingress_rules=None, egress_rules=None):
        """
        보안 리스트 생성 메소드
        """
        return oci.core.SecurityList(
            resource_name=name,
            compartment_id=cfg.COMPARTMENT_ID,
            vcn_id=self.vcn.id,
            ingress_security_rules=ingress_rules,
            egress_security_rules=egress_rules,
            display_name=name,
        )

    def create_node_security_list(self):
        """
        노드용 보안 리스트 생성 메소드
        """
        return self.create_security_list(
            name='oke-node-security-list',
            ingress_rules=self.get_node_ingress_rules(),
            egress_rules=self.get_node_egress_rules(),
        )

    def create_k8s_api_security_list(self):
        """
        Kubernetes API 보안 리스트 생성 메소드
        """
        return self.create_security_list(
            name='oke-k8s-api-security-list',
            ingress_rules=self.get_k8s_api_ingress_rules(),
            egress_rules=self.get_k8s_api_egress_rules(),
        )

    def create_service_lb_security_list(self):
        """
        서비스 로드 밸런서 보안 리스트 생성 메소드
        """
        return self.create_security_list(name='oke-service-lb-security-list')

    # 공통 규칙 생성 메소드
    def path_discovery_rule(self, source_or_dest, cidr_block):
        """
        Path discovery 규칙 생성 메소드
        """
        return {
            'description': 'Path discovery',
            'icmp_options': {'code': 4, 'type': 3},
            'protocol': '1',
            source_or_dest: cidr_block,
            'stateless': False,
        }

    def node_tcp_rule(self):
        """
        노드 TCP 규칙 생성 메소드
        """
        return {
            'description': 'TCP access from Kubernetes Control Plane',
            'protocol': '6',
            'source': cfg.K8S_API_SUBNET_CIDR_BLOCK,
            'stateless': False,
        }

    # 노드용 Ingress 규칙 생성 메소드
    def get_node_ingress_rules(self):
        """
        노드용 Ingress 규칙 생성
        """
        return [
            self.path_discovery_rule('source', cfg.K8S_API_SUBNET_CIDR_BLOCK),
            self.node_tcp_rule(),
            {
                'description': 'Inbound SSH traffic to worker nodes',
                'protocol': '6',
                'source': '0.0.0.0/0',
                'stateless': False,
            },
            {
                'description': 'Allow pods on one worker node to communicate with pods on other worker nodes',
                'protocol': 'all',
                'source': cfg.NODE_SUBNET_CIDR_BLOCK,
                'stateless': False,
            },
        ]

    # 노드용 Egress 규칙 생성 메소드
    def get_node_egress_rules(self):
        """
        노드용 Egress 규칙 생성
        """
        return [
            self.path_discovery_rule('destination', cfg.K8S_API_SUBNET_CIDR_BLOCK),
            {
                'description': 'Allow nodes to communicate with OKE',
                'destination': cfg.SERVICE_CIDR,
                'destination_type': 'SERVICE_CIDR_BLOCK',
                'protocol': '6',
                'stateless': False,
            },
            {
                'description': 'Allow pods on one worker node to communicate with pods on other worker nodes',
                'destination': cfg.NODE_SUBNET_CIDR_BLOCK,
                'destination_type': 'CIDR_BLOCK',
                'protocol': 'all',
                'stateless': False,
            },
            {
                'description': 'Access to Kubernetes API Endpoint',
                'destination': cfg.K8S_API_SUBNET_CIDR_BLOCK,
                'destination_type': 'CIDR_BLOCK',
                'protocol': '6',
                'stateless': False,
            },
            {
                'description': 'Worker Nodes access to Internet',
                'destination': '0.0.0.0/0',
                'destination_type': 'CIDR_BLOCK',
                'protocol': 'all',
                'stateless': False,
            },
        ]

    # Kubernetes API Ingress 규칙 생성 메소드
    def get_k8s_api_ingress_rules(self):
        """
        Kubernetes API Ingress 규칙 생성
        """
        return [
            self.path_discovery_rule('source', cfg.NODE_SUBNET_CIDR_BLOCK),
            {
                'description': 'External access to Kubernetes API endpoint',
                'protocol': '6',
                'source': '0.0.0.0/0',
                'stateless': False,
            },
            {
                'description': 'Kubernetes worker to Kubernetes API endpoint communication',
                'protocol': '6',
                'source': cfg.NODE_SUBNET_CIDR_BLOCK,
                'stateless': False,
            },
        ]

    # Kubernetes API Egress 규칙 생성 메소드
    def get_k8s_api_egress_rules(self):
        """
        Kubernetes API Egress 규칙 생성
        """
        return [
            self.path_discovery_rule('destination', cfg.NODE_SUBNET_CIDR_BLOCK),
            {
                'description': 'Allow Kubernetes Control Plane to communicate with OKE',
                'destination': cfg.SERVICE_CIDR,
                'destination_type': 'SERVICE_CIDR_BLOCK',
                'protocol': '6',
                'stateless': False,
            },
            {
                'description': 'All traffic to worker nodes',
                'destination': cfg.NODE_SUBNET_CIDR_BLOCK,
                'destination_type': 'CIDR_BLOCK',
                'protocol': '6',
                'stateless': False,
            },
        ]

    def create_all_security_lists(self):
        """
        모든 보안 리스트를 생성하는 메소드
        """
        self.node_security_list = self.create_node_security_list()
        self.k8s_api_security_list = self.create_k8s_api_security_list()
        self.service_lb_security_list = self.create_service_lb_security_list()
        return (
            self.node_security_list,
            self.k8s_api_security_list,
            self.service_lb_security_list,
        )
