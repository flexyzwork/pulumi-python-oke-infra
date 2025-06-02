# Pulumi를 사용한 OCI OKE 관리 가이드

이 문서는 Pulumi를 사용하여 Oracle Cloud Infrastructure(OCI)에서 Oracle Kubernetes Engine(OKE) 클러스터를 생성하고, Cluster API를 통해 전체 인프라를 관리하는 방법을 설명합니다.

## 🎯 왜 만들었나요?

### 기존 문제점
- **수동 관리의 한계**: 웹 콘솔을 통한 수동 인프라 관리로 인한 실수와 일관성 부족
- **환경 간 불일치**: 개발, 스테이징, 프로덕션 환경 간의 설정 차이
- **복잡한 멀티 클러스터 관리**: 여러 Kubernetes 클러스터의 생명주기 관리 복잡성

### 해결 방안
- **Infrastructure as Code**: 모든 인프라를 코드로 정의하여 버전 관리 및 재현 가능한 배포
- **자동화된 워크플로우**: Pulumi + Cluster API를 통한 선언적 인프라 관리
- **표준화된 환경**: 동일한 템플릿으로 일관된 클러스터 환경 제공

### 기대 효과
```
시간 단축: 클러스터 생성 4-6시간 → 15-30분
운영 효율: 수동 작업 최소화 및 자동화된 장애 복구
비용 절감: 리소스 최적화 및 운영 인력 절약
```

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Pulumi 설치 및 설정](#pulumi-설치-및-설정)
3. [OCI CLI 설정](#oci-cli-설정)
4. [Python 환경 설정](#python-환경-설정)
5. [Pulumi 스택 설정](#pulumi-스택-설정)
6. [인프라 배포](#인프라-배포)
7. [문제 해결](#문제-해결)

## 🚀 사전 준비

### 시스템 요구사항
- macOS/Linux/Windows
- Python 3.8 이상
- Node.js 14 이상
- Docker (선택사항)

### 필요한 도구
- Pulumi CLI
- OCI CLI
- kubectl
- Python 가상환경 (venv)

## 🔧 Pulumi 설치 및 설정

### 1. Pulumi 설치

```bash
# macOS (Homebrew 사용)
brew install pulumi/tap/pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows (Chocolatey 사용)
choco install pulumi
```

### 2. Pulumi 조직 설정 (선택사항)

```bash
# 기본 조직 설정
pulumi org set-default <your-organization-name>
```

### 3. Terraform에서 Pulumi로 변환 (기존 Terraform 코드가 있는 경우)

```bash
# Terraform을 Pulumi Python 코드로 변환
pulumi convert --from terraform --language python
```

> ⚠️ **주의**: 이 명령어는 `pulumi new python`과 유사한 효과를 발생시켜 기존 파일(`__main__.py`, `.gitignore` 등)을 덮어쓸 수 있습니다.

## 🌩️ OCI CLI 설정

### 1. OCI CLI 설치

```bash
# macOS (Homebrew 사용)
brew install oci-cli

# Linux/Windows
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

### 2. OCI 설정 파일 구성

```bash
# OCI 설정 초기화
oci setup config

# 설정 파일 확인
cat ~/.oci/config
```

### 3. OCI 프로필 설정

```bash
# 기본 프로필을 'os'로 변경
vi ~/.oci/oci_cli_rc
```

**oci_cli_rc 파일 내용:**
```ini
[OCI_CLI_SETTINGS]
default_profile=os
```

### 4. OCI 연결 확인

```bash
# 프로필 변경 확인
echo $OCI_CLI_PROFILE

# 사용자 정보 확인
oci iam user get --user-id $(oci iam user list --query "data[?\"lifecycle-state\"=='ACTIVE'].id | [0]" --raw-output)

# 세션 유효성 검증
oci session validate
```

## 🐍 Python 환경 설정

### 1. 가상환경 생성 및 활성화

```bash
# make를 사용한 가상환경 생성 및 활성화
make venv

# 또는

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 2. 의존성 설치

```bash
# Make를 사용한 설치
make install
```

### 3. VS Code Python 인터프리터 설정

1. `Cmd + Shift + P` (macOS) 또는 `Ctrl + Shift + P` (Windows/Linux)
2. `Python: Select Interpreter` 선택
3. `venv` 환경 선택

## 📦 Pulumi 스택 설정

### 1. 새로운 스택 생성

```bash
# 프로덕션 스택 초기화
pulumi stack init prod --
```

### 2. 구성 값 설정

```bash
chmod +x ./setup_config.sh
./setup_config.sh
```

> 📝 **참고**: 이 스크립트를 실행하면 `Pulumi.prod.yaml` 파일에 설정값이 저장됩니다.

### 3. 스택 관리

```bash
# 모든 스택 확인
pulumi stack ls -a

# 스택 삭제 (필요한 경우)
pulumi stack rm prod
```

## 🚀 인프라 배포

### 1. 인프라 배포 실행

```bash
# 모든 리소스 배포
make up

# 또는 직접 Pulumi 명령 사용
pulumi up
```

### 2. 배포 상태 확인

```bash
# 스택 상태 확인
pulumi stack

# 출력 값 확인
pulumi stack output

# 리소스 상태 확인
pulumi stack export
```

### 3. kubeconfig 설정

```bash
# OKE 클러스터의 kubeconfig 획득
oci ce cluster create-kubeconfig \
    --cluster-id $(pulumi stack output cluster_id) \
    --file ~/.kube/config \
    --region ap-osaka-1 \
    --token-version 2.0.0

# kubectl 연결 확인
kubectl get nodes
```

## 📊 모니터링 및 로깅

### 1. 클러스터 상태 모니터링

```bash
# OKE 클러스터 상태 확인
oci ce cluster get --cluster-id $(pulumi stack output cluster_id)

# 노드 풀 상태 확인
oci ce node-pool get --node-pool-id $(pulumi stack output node_pool_id)
```

### 2. 로그 확인

```bash
# Pulumi 로그 확인
pulumi logs

# OCI 감사 로그 확인 (웹 콘솔)
# OCI Console > Governance & Administration > Audit
```

## 🧹 리소스 정리

### 1. 인프라 삭제

```bash
# 모든 리소스 삭제
pulumi destroy

# 확인 후 실행
pulumi destroy --yes
```

### 2. 스택 삭제

```bash
# 스택 삭제
pulumi stack rm dev
```

## 🛠️ 문제 해결

### 1. 일반적인 문제

#### OCI 인증 문제
```bash
# OCI 설정 확인
oci setup repair-file-permissions --file ~/.oci/config
oci setup repair-file-permissions --file ~/.oci/oci_api_key.pem
```

#### Pulumi 상태 문제
```bash
# 상태 새로고침
pulumi refresh

# 상태 복구
pulumi stack import
```

#### Kubernetes 연결 문제
```bash
# kubeconfig 재생성
oci ce cluster create-kubeconfig \
    --cluster-id <cluster-id> \
    --file ~/.kube/config \
    --region ap-osaka-1 \
    --overwrite
```

### 2. 디버깅

```bash
# Pulumi 디버그 모드
pulumi up --debug

```

## 📚 참고 자료

- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
- [Pulumi OCI Provider](https://www.pulumi.com/registry/packages/oci/)
- [OCI Container Engine for Kubernetes](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [OCI CLI 공식 문서](https://docs.oracle.com/en-us/iaas/tools/oci-cli/3.43.1/oci_cli_docs/)

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여

버그 리포트, 기능 요청, 풀 리퀘스트는 언제든지 환영합니다!

---

**작성자**: Flexyz
**이메일**: contact@flexyz.work
**깃헙**: https://github.com/flexyzwork
**웹사이트**: https://flexyz.work
**최종 업데이트**: 2025년 6월 2일
**버전**: 1.0.0

<br />
<br />



---


# Pulumi OCI OKE Management Guide

This document explains how to create Oracle Kubernetes Engine (OKE) clusters on Oracle Cloud Infrastructure (OCI) using Pulumi and manage the entire infrastructure through Cluster API.

## 🎯 Why We Built This

### Existing Problems
- **Manual Management Limitations**: Errors and lack of consistency due to manual infrastructure management through web console
- **Environment Inconsistency**: Configuration differences between development, staging, and production environments
- **Complex Multi-Cluster Management**: Complexity in managing the lifecycle of multiple Kubernetes clusters

### Solution
- **Infrastructure as Code**: Define all infrastructure as code for version control and reproducible deployments
- **Automated Workflows**: Declarative infrastructure management through Pulumi + Cluster API
- **Standardized Environments**: Consistent cluster environments using identical templates

### Expected Benefits
```
Time Reduction: Cluster creation 4-6 hours → 15-30 minutes
Operational Efficiency: Minimize manual work and automated failure recovery
Cost Savings: Resource optimization and operational workforce reduction
```

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pulumi Installation and Setup](#pulumi-installation-and-setup)
3. [OCI CLI Setup](#oci-cli-setup)
4. [Python Environment Setup](#python-environment-setup)
5. [Pulumi Stack Configuration](#pulumi-stack-configuration)
6. [Infrastructure Deployment](#infrastructure-deployment)
7. [Troubleshooting](#troubleshooting)

## 🚀 Prerequisites

### System Requirements
- macOS/Linux/Windows
- Python 3.8 or higher
- Node.js 14 or higher
- Docker (optional)

### Required Tools
- Pulumi CLI
- OCI CLI
- kubectl
- Python virtual environment (venv)

## 🔧 Pulumi Installation and Setup

### 1. Install Pulumi

```bash
# macOS (using Homebrew)
brew install pulumi/tap/pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows (using Chocolatey)
choco install pulumi
```

### 2. Pulumi Organization Setup (Optional)

```bash
# Set default organization
pulumi org set-default codelab-kr
```

### 3. Convert from Terraform to Pulumi (if you have existing Terraform code)

```bash
# Convert Terraform to Pulumi Python code
pulumi convert --from terraform --language python
```

> ⚠️ **Warning**: This command has a similar effect to `pulumi new python` and may overwrite existing files (`__main__.py`, `.gitignore`, etc.).

## 🌩️ OCI CLI Setup

### 1. Install OCI CLI

```bash
# macOS (using Homebrew)
brew install oci-cli

# Linux/Windows
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
```

### 2. Configure OCI Configuration File

```bash
# Initialize OCI configuration
oci setup config

# Check configuration file
cat ~/.oci/config
```

### 3. Set OCI Profile

```bash
# Change default profile to 'os'
vi ~/.oci/oci_cli_rc
```

**oci_cli_rc file content:**
```ini
[OCI_CLI_SETTINGS]
default_profile=os
```

### 4. Verify OCI Connection

```bash
# Check profile change
echo $OCI_CLI_PROFILE

# Check user information
oci iam user get --user-id $(oci iam user list --query "data[?\"lifecycle-state\"=='ACTIVE'].id | [0]" --raw-output)

# Validate session
oci session validate
```

## 🐍 Python Environment Setup

### 1. Create and Activate Virtual Environment

```bash
# Create and activate virtual environment using make
make venv

# Or manually

# Create virtual environment
python -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install using Make
make install
```

### 3. VS Code Python Interpreter Setup

1. Press `Cmd + Shift + P` (macOS) or `Ctrl + Shift + P` (Windows/Linux)
2. Select `Python: Select Interpreter`
3. Choose the `venv` environment

## 📦 Pulumi Stack Configuration

### 1. Create New Stack

```bash
# Initialize production stack
pulumi stack init prod
```

### 2. Set Configuration Values

```bash
chmod +x ./setup_config.sh
./setup_config.sh
```

> 📝 **Note**: These settings are stored in the `Pulumi.prod.yaml` file.

### 3. Stack Management

```bash
# Check all stacks
pulumi stack ls -a

# Delete stack (if needed)
pulumi stack rm dev
```

## 🚀 Infrastructure Deployment

### 1. Execute Infrastructure Deployment

```bash
# Deploy all resources
make up

# Or use Pulumi command directly
pulumi up
```

### 2. Check Deployment Status

```bash
# Check stack status
pulumi stack

# Check output values
pulumi stack output

# Check resource status
pulumi stack export
```

### 3. Configure kubeconfig

```bash
# Obtain kubeconfig for OKE cluster
oci ce cluster create-kubeconfig \
    --cluster-id $(pulumi stack output cluster_id) \
    --file ~/.kube/config \
    --region ap-osaka-1 \
    --token-version 2.0.0

# Verify kubectl connection
kubectl get nodes
```

## 📊 Monitoring and Logging

### 1. Monitor Cluster Status

```bash
# Check OKE cluster status
oci ce cluster get --cluster-id $(pulumi stack output cluster_id)

# Check node pool status
oci ce node-pool get --node-pool-id $(pulumi stack output node_pool_id)
```

### 2. Check Logs

```bash
# Check Pulumi logs
pulumi logs

# Check OCI audit logs (web console)
# OCI Console > Governance & Administration > Audit
```

## 🧹 Resource Cleanup

### 1. Delete Infrastructure

```bash
# Delete all resources
pulumi destroy

# Execute with confirmation
pulumi destroy --yes
```

### 2. Delete Stack

```bash
# Delete stack
pulumi stack rm dev
```

## 🛠️ Troubleshooting

### 1. Common Issues

#### OCI Authentication Issues
```bash
# Check OCI configuration
oci setup repair-file-permissions --file ~/.oci/config
oci setup repair-file-permissions --file ~/.oci/oci_api_key.pem
```

#### Pulumi State Issues
```bash
# Refresh state
pulumi refresh

# Recover state
pulumi stack import
```

#### Kubernetes Connection Issues
```bash
# Regenerate kubeconfig
oci ce cluster create-kubeconfig \
    --cluster-id <cluster-id> \
    --file ~/.kube/config \
    --region ap-osaka-1 \
    --overwrite
```

### 2. Debugging

```bash
# Pulumi debug mode
pulumi up --debug
```

## 📚 References

- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
- [Pulumi OCI Provider](https://www.pulumi.com/registry/packages/oci/)
- [OCI Container Engine for Kubernetes](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [OCI CLI Official Documentation](https://docs.oracle.com/en-us/iaas/tools/oci-cli/3.43.1/oci_cli_docs/)

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Bug reports, feature requests, and pull requests are always welcome!

---

**Author**: flexyz
**Email**: contact@flexyz.work
**GitHub**: https://github.com/flexyzwork
**Website**: https://flexyz.work
**Last Updated**: 2th June 2025
**Version**: 1.0.0
