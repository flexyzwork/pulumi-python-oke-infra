import pulumi_oci as oci

import config as cfg


class NodePoolManager:
    """
    OKE 노드 풀 생성 및 관리 클래스
    """

    def __init__(self, oke_cluster, node_subnet):
        self.oke_cluster = oke_cluster
        self.node_subnet = node_subnet
        self.node_pool = None

    def create_node_config_details(self):
        """
        OKE 노드 풀의 구성 세부 정보를 생성하는 메소드
        """
        return oci.containerengine.NodePoolNodeConfigDetailsArgs(
            freeform_tags={'oke_node_pool_name': cfg.NODE_POOL_NAME},
            node_pool_pod_network_option_details=oci.containerengine.NodePoolNodeConfigDetailsNodePoolPodNetworkOptionDetailsArgs(
                pod_subnet_ids=[self.node_subnet.id], cni_type='OCI_VCN_IP_NATIVE'
            ),
            placement_configs=[
                oci.containerengine.NodePoolNodeConfigDetailsPlacementConfigArgs(
                    availability_domain=cfg.AVAILABILITY_DOMAIN,
                    subnet_id=self.node_subnet.id,
                )
            ],
            size=cfg.NODE_POOL_SIZE,  # 노드 풀 크기 (Node pool size)
        )

    def create_node_pool(self):
        """
        OKE 노드 풀을 생성하는 메소드
        """
        self.node_pool = oci.containerengine.NodePool(
            'oke-node-pool',
            cluster_id=self.oke_cluster.id,
            compartment_id=cfg.COMPARTMENT_ID,
            freeform_tags={'OKEnodePoolName': cfg.NODE_POOL_NAME},
            initial_node_labels=[oci.containerengine.NodePoolInitialNodeLabelArgs(key='name', value='mgmt')],
            kubernetes_version=cfg.KUBERNETES_VERSION,
            name=cfg.NODE_POOL_NAME,
            node_config_details=self.create_node_config_details(),
            node_eviction_node_pool_settings=oci.containerengine.NodePoolNodeEvictionNodePoolSettingsArgs(
                eviction_grace_duration='PT60M'  # 노드 제거 설정 (Node eviction settings)
            ),
            node_shape=cfg.NODE_SHAPE,
            node_shape_config=oci.containerengine.NodePoolNodeShapeConfigArgs(
                memory_in_gbs=cfg.NODE_MEMORY_GBS, ocpus=cfg.NODE_OCPUS
            ),
            node_source_details=oci.containerengine.NodePoolNodeSourceDetailsArgs(
                image_id=cfg.IMAGE_ID, source_type='IMAGE'
            ),
            ssh_public_key=cfg.SSH_PUBLIC_KEY,  # SSH 공개 키
        )
        return self.node_pool
