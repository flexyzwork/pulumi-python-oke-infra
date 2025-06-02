# ruff: noqa: E501
"""
개선된 OCI 설정 관리
민감한 정보는 Pulumi config에서, 나머지는 여기서 관리
"""

from typing import Any

import pulumi
from pulumi import Output


class OCIConfig:
    """OCI 설정을 관리하는 클래스"""

    def __init__(self):
        self.config = pulumi.Config()
        self._validate_required_configs()

    def _validate_required_configs(self) -> None:
        """필수 설정값 검증"""
        required_secrets = ['compartment_id', 'ssh_public_key']
        missing_configs = []

        for key in required_secrets:
            try:
                value: Output[str] = self.config.require_secret(key)
                # Output 객체는 bool 평가를 직접 할 수 없으므로, None 체크만 수행
                if value is None:
                    missing_configs.append(key)
            except Exception:
                missing_configs.append(key)

        if missing_configs:
            raise ValueError(
                f'다음 필수 설정이 누락되었습니다: {", ".join(missing_configs)}\n'
                'setup_config.sh 스크립트를 실행하여 설정하세요.'
            )

    # =============================================================================
    # Pulumi config에서 가져오는 민감한 정보
    # =============================================================================

    @property
    def compartment_id(self) -> Output[str]:
        """OCI 구획 ID (민감한 정보)"""
        result: Output[str] = self.config.require_secret('compartment_id')
        return result

    @property
    def ssh_public_key(self) -> Output[str]:
        """SSH 공개 키 (민감한 정보)"""
        result: Output[str] = self.config.require_secret('ssh_public_key')
        return result

    @property
    def region(self) -> str:
        """OCI 리전"""
        return self.config.get('region') or 'ap-osaka-1'

    @property
    def profile(self) -> str:
        """OCI CLI 프로필"""
        return self.config.get('profile') or 'DEFAULT'

    # =============================================================================
    # 리전별 동적 설정
    # =============================================================================

    @property
    def region_config(self) -> dict[str, Any]:
        """리전별 설정 반환"""
        region_configs = {
            'ap-osaka-1': {
                'availability_domain': 'PCHh:AP-OSAKA-1-AD-1',
                'service_id': 'ocid1.service.oc1.ap-osaka-1.aaaaaaaanpw2x646vasmcdktlznzhf7mwmcgf4hhmw5zepgspmseokxjyj4q',
                'image_id': 'ocid1.image.oc1.ap-osaka-1.aaaaaaaa4xyxytwqlwbxp5rp5qvhi5snlomtjgyavitu3m36bp4neknjsloa',
            },
            'ap-seoul-1': {
                'availability_domain': 'YnyK:AP-SEOUL-1-AD-1',
                'service_id': 'ocid1.service.oc1.ap-seoul-1.aaaaaaaac4kj7ddh5y7kfqbfzc6hzxfazezmvr4n6k7rqt7ifrfcjxnb2y4q',
                'image_id': 'ocid1.image.oc1.ap-seoul-1.aaaaaaaas5x3bpjnktaajrr7mvqjr3kh4zegqlqeqe5wbql4dqq4q2qj2o5a',
            },
            'ap-tokyo-1': {
                'availability_domain': 'bJmJ:AP-TOKYO-1-AD-1',
                'service_id': 'ocid1.service.oc1.ap-tokyo-1.aaaaaaaanp2x646vasmcdktlznzhf7mwmcgf4hhmw5zepgspmseokxjyj4q',
                'image_id': 'ocid1.image.oc1.ap-tokyo-1.aaaaaaaa4xyxytwqlwbxp5rp5qvhi5snlomtjgyavitu3m36bp4neknjsloa',
            },
            'us-ashburn-1': {
                'availability_domain': 'ZwDO:US-ASHBURN-1-AD-1',
                'service_id': 'ocid1.service.oc1.us-ashburn-1.aaaaaaaanp2x646vasmcdktlznzhf7mwmcgf4hhmw5zepgspmseokxjyj4q',
                'image_id': 'ocid1.image.oc1.us-ashburn-1.aaaaaaaa4xyxytwqlwbxp5rp5qvhi5snlomtjgyavitu3m36bp4neknjsloa',
            },
            'us-phoenix-1': {
                'availability_domain': 'RWDJ:US-PHOENIX-1-AD-1',
                'service_id': 'ocid1.service.oc1.us-phoenix-1.aaaaaaaanp2x646vasmcdktlznzhf7mwmcgf4hhmw5zepgspmseokxjyj4q',
                'image_id': 'ocid1.image.oc1.us-phoenix-1.aaaaaaaa4xyxytwqlwbxp5rp5qvhi5snlomtjgyavitu3m36bp4neknjsloa',
            },
        }

        config = region_configs.get(self.region)
        if not config:
            pulumi.log.warn(f"리전 '{self.region}'에 대한 설정을 찾을 수 없습니다. 기본값을 사용합니다.")
            return region_configs['ap-osaka-1']

        return config

    @property
    def availability_domain(self) -> str:
        """현재 리전의 가용성 도메인"""
        domain = self.region_config['availability_domain']
        assert isinstance(domain, str), 'availability_domain must be a string'
        return domain

    @property
    def service_id(self) -> str:
        """현재 리전의 서비스 ID"""
        service_id = self.region_config['service_id']
        assert isinstance(service_id, str), 'service_id must be a string'
        return service_id

    @property
    def image_id(self) -> str:
        """현재 리전의 이미지 ID"""
        image_id = self.region_config['image_id']
        assert isinstance(image_id, str), 'image_id must be a string'
        return image_id

    # =============================================================================
    # 네트워크 설정
    # =============================================================================

    @property
    def vcn_cidr_block(self) -> str:
        """VCN CIDR 블록"""
        return self.config.get('vcn_cidr_block') or '10.0.0.0/16'

    @property
    def kubernetes_version(self) -> str:
        """Kubernetes 버전"""
        return self.config.get('kubernetes_version') or 'v1.32.1'

    @property
    def service_cidr(self) -> str:
        """서비스 CIDR"""
        return 'all-kix-services-in-oracle-services-network'

    # =============================================================================
    # VCN 리소스 이름
    # =============================================================================

    @property
    def vcn_display_name(self) -> str:
        """VCN 표시 이름"""
        return self.config.get('vcn_display_name') or 'oke-vcn-mgmt'

    @property
    def internet_gateway_display_name(self) -> str:
        """인터넷 게이트웨이 표시 이름"""
        return self.config.get('igw_display_name') or 'oke-igw-mgmt'

    @property
    def nat_gateway_display_name(self) -> str:
        """NAT 게이트웨이 표시 이름"""
        return self.config.get('ngw_display_name') or 'oke-ngw-mgmt'

    @property
    def service_gateway_display_name(self) -> str:
        """서비스 게이트웨이 표시 이름"""
        return self.config.get('sgw_display_name') or 'oke-sgw-mgmt'

    # =============================================================================
    # 서브넷 설정
    # =============================================================================

    @property
    def service_lb_subnet_cidr_block(self) -> str:
        """서비스 로드밸런서 서브넷 CIDR"""
        return self.config.get('service_lb_subnet_cidr') or '10.0.20.0/24'

    @property
    def node_subnet_cidr_block(self) -> str:
        """노드 서브넷 CIDR"""
        return self.config.get('node_subnet_cidr') or '10.0.10.0/24'

    @property
    def k8s_api_subnet_cidr_block(self) -> str:
        """Kubernetes API 서브넷 CIDR"""
        return self.config.get('k8s_api_subnet_cidr') or '10.0.0.0/28'

    # =============================================================================
    # 노드 풀 설정
    # =============================================================================

    @property
    def node_pool_name(self) -> str:
        """노드 풀 이름"""
        return self.config.get('node_pool_name') or 'pool1'

    @property
    def node_pool_size(self) -> int:
        """노드 풀 크기"""
        return self.config.get_int('node_pool_size') or 2

    @property
    def node_shape(self) -> str:
        """노드 인스턴스 모양"""
        return self.config.get('node_shape') or 'VM.Standard.A1.Flex'

    @property
    def node_memory_gbs(self) -> int:
        """노드 메모리 GB"""
        return self.config.get_int('node_memory_gbs') or 12

    @property
    def node_ocpus(self) -> int:
        """노드 OCPU 수"""
        return self.config.get_int('node_ocpus') or 2

    # =============================================================================
    # 유틸리티 메서드
    # =============================================================================

    def get_all_config(self) -> dict[str, Any]:
        """모든 설정을 딕셔너리로 반환 (민감한 정보 제외)"""
        return {
            'region': self.region,
            'profile': self.profile,
            'availability_domain': self.availability_domain,
            'vcn_cidr_block': self.vcn_cidr_block,
            'kubernetes_version': self.kubernetes_version,
            'vcn_display_name': self.vcn_display_name,
            'service_lb_subnet_cidr_block': self.service_lb_subnet_cidr_block,
            'node_subnet_cidr_block': self.node_subnet_cidr_block,
            'k8s_api_subnet_cidr_block': self.k8s_api_subnet_cidr_block,
            'node_pool_name': self.node_pool_name,
            'node_pool_size': self.node_pool_size,
            'node_shape': self.node_shape,
            'node_memory_gbs': self.node_memory_gbs,
            'node_ocpus': self.node_ocpus,
        }

    def validate_cidr_blocks(self) -> None:
        """CIDR 블록들이 겹치지 않는지 검증"""
        import ipaddress

        try:
            vcn_network = ipaddress.IPv4Network(self.vcn_cidr_block)
            service_lb_network = ipaddress.IPv4Network(self.service_lb_subnet_cidr_block)
            node_network = ipaddress.IPv4Network(self.node_subnet_cidr_block)
            k8s_api_network = ipaddress.IPv4Network(self.k8s_api_subnet_cidr_block)

            # VCN 내에 모든 서브넷이 포함되는지 확인
            subnets = [service_lb_network, node_network, k8s_api_network]

            for subnet in subnets:
                if not subnet.subnet_of(vcn_network):
                    raise ValueError(f'서브넷 {subnet}이 VCN {vcn_network} 범위를 벗어났습니다.')

            # 서브넷들이 서로 겹치지 않는지 확인
            for i, subnet1 in enumerate(subnets):
                for subnet2 in subnets[i + 1 :]:
                    if subnet1.overlaps(subnet2):
                        raise ValueError(f'서브넷 {subnet1}과 {subnet2}가 겹칩니다.')

            pulumi.log.info('모든 CIDR 블록 검증이 완료되었습니다.')

        except ValueError as e:
            pulumi.log.error(f'CIDR 블록 검증 실패: {e}')
            raise


# 전역 설정 인스턴스 생성
cfg = OCIConfig()

# 하위 호환성을 위한 기존 변수들 (deprecated)
COMPARTMENT_ID = cfg.compartment_id
SSH_PUBLIC_KEY = cfg.ssh_public_key
REGION = cfg.region
PROFILE = cfg.profile
VCN_CIDR_BLOCK = cfg.vcn_cidr_block
KUBERNETES_VERSION = cfg.kubernetes_version
SERVICE_CIDR = cfg.service_cidr
AVAILABILITY_DOMAIN = cfg.availability_domain
SERVICE_ID = cfg.service_id
IMAGE_ID = cfg.image_id
VCN_DISPLAY_NAME = cfg.vcn_display_name
INTERNET_GATEWAY_DISPLAY_NAME = cfg.internet_gateway_display_name
NAT_GATEWAY_DISPLAY_NAME = cfg.nat_gateway_display_name
SERVICE_GATEWAY_DISPLAY_NAME = cfg.service_gateway_display_name
SERVICE_LB_SUBNET_CIDR_BLOCK = cfg.service_lb_subnet_cidr_block
NODE_SUBNET_CIDR_BLOCK = cfg.node_subnet_cidr_block
K8S_API_SUBNET_CIDR_BLOCK = cfg.k8s_api_subnet_cidr_block
NODE_POOL_NAME = cfg.node_pool_name
NODE_POOL_SIZE = cfg.node_pool_size
NODE_SHAPE = cfg.node_shape
NODE_MEMORY_GBS = cfg.node_memory_gbs
NODE_OCPUS = cfg.node_ocpus

# 설정 검증 실행
if __name__ != '__main__':
    try:
        cfg.validate_cidr_blocks()
    except Exception as e:
        pulumi.log.warn(f'설정 검증 중 경고: {e}')
