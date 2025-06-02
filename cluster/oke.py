import pulumi
import pulumi_oci as oci

import config as cfg


class OKEClusterManager:
    """
    OKE 클러스터 생성 및 관리 클래스
    """

    def __init__(self, vcn, k8s_api_subnet, service_lb_subnet):
        self.vcn = vcn
        self.k8s_api_subnet = k8s_api_subnet
        self.service_lb_subnet = service_lb_subnet
        self.cluster = None

    def create_cluster(self):
        """
        OKE 클러스터를 생성하는 메소드
        """
        self.cluster = oci.containerengine.Cluster(
            'oke-cluster',
            compartment_id=cfg.COMPARTMENT_ID,
            name='mgmt-cluster',
            kubernetes_version=cfg.KUBERNETES_VERSION,
            vcn_id=self.vcn.id,
            options=oci.containerengine.ClusterOptionsArgs(service_lb_subnet_ids=[self.service_lb_subnet.id]),
            endpoint_config=oci.containerengine.ClusterEndpointConfigArgs(
                is_public_ip_enabled=True, subnet_id=self.k8s_api_subnet.id
            ),
            cluster_pod_network_options=[
                oci.containerengine.ClusterClusterPodNetworkOptionArgs(cni_type='OCI_VCN_IP_NATIVE')
            ],
            freeform_tags={'OKEclusterName': 'mgmt'},
            type='BASIC_CLUSTER',
        )

        # 클러스터 ID를 Pulumi로 export
        pulumi.export('oke_cluster_id', self.cluster.id)

        return self.cluster
