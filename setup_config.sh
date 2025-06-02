#!/bin/bash
# 개선된 Pulumi 설정 스크립트

set -e  # 오류 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${CYAN}🔐 Pulumi OCI 설정을 시작합니다...${NC}"
echo ""

# Pulumi 설치 확인
if ! command -v pulumi &> /dev/null; then
    log_error "Pulumi가 설치되지 않았습니다."
    log_info "https://www.pulumi.com/docs/get-started/install/ 에서 설치하세요."
    exit 1
fi

# 현재 디렉토리에 Pulumi.yaml이 있는지 확인
if [ ! -f "Pulumi.yaml" ]; then
    log_error "Pulumi.yaml 파일을 찾을 수 없습니다."
    log_info "먼저 'pulumi new' 명령어로 프로젝트를 초기화하세요."
    exit 1
fi

# 스택 확인 및 선택/생성
setup_stack() {
    log_info "Pulumi 스택을 확인합니다..."

    # 현재 스택 확인
    if pulumi stack ls &>/dev/null; then
        local current_stack=$(pulumi stack ls --json 2>/dev/null | jq -r '.[] | select(.current == true) | .name' 2>/dev/null || echo "")

        if [ -n "$current_stack" ]; then
            log_info "현재 스택: $current_stack"
            echo -n "이 스택을 사용하시겠습니까? [Y/n]: "
            read -r use_current
            if [[ "$use_current" =~ ^[Nn]$ ]]; then
                current_stack=""
            fi
        fi

        if [ -z "$current_stack" ]; then
            echo ""
            log_info "사용 가능한 스택 목록:"
            pulumi stack ls
            echo ""
            echo -n "사용할 스택 이름을 입력하세요 (새로 만들려면 신규 이름): "
            read -r stack_name

            if [ -z "$stack_name" ]; then
                log_error "스택 이름이 필요합니다."
                exit 1
            fi

            # 스택 존재 확인
            if pulumi stack ls --json 2>/dev/null | jq -e ".[] | select(.name == \"$stack_name\")" >/dev/null 2>&1; then
                log_info "기존 스택 '$stack_name'을 선택합니다."
                pulumi stack select "$stack_name"
            else
                log_info "새 스택 '$stack_name'을 생성합니다."
                pulumi stack init "$stack_name"
            fi
        fi
    else
        echo -n "새 스택 이름을 입력하세요 [prod]: "
        read -r stack_name
        stack_name=${stack_name:-prod}
        log_info "스택 '$stack_name'을 생성합니다."
        pulumi stack init "$stack_name"
    fi

    log_success "스택 설정 완료!"
    echo ""
}

# 민감한 정보 설정
setup_secrets() {
    log_info "민감한 정보를 설정합니다..."
    echo ""

    # 구획 ID 설정
    echo -n "OCI 구획 ID 입력: "
    read -r COMPARTMENT_ID
    if [ -z "$COMPARTMENT_ID" ]; then
        log_error "구획 ID는 필수입니다."
        exit 1
    fi

    # OCID 형식 검증 (간단한 체크)
    if [[ ! "$COMPARTMENT_ID" =~ ^ocid1\.compartment\.oc1\.\. ]]; then
        log_warning "구획 ID 형식이 올바르지 않을 수 있습니다."
        echo -n "계속하시겠습니까? [y/N]: "
        read -r continue_anyway
        if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    pulumi config set --secret compartment_id "$COMPARTMENT_ID"
    log_success "구획 ID 설정 완료"

    # SSH 키 설정
    echo ""
    echo "SSH 공개 키를 입력하세요."
    echo "파일에서 읽으려면 파일 경로를 입력하세요 (예: ~/.ssh/id_rsa.pub):"
    read -r SSH_KEY_INPUT

    if [ -z "$SSH_KEY_INPUT" ]; then
        log_error "SSH 키는 필수입니다."
        exit 1
    fi

    # 파일 경로인지 확인
    if [ -f "$SSH_KEY_INPUT" ]; then
        SSH_KEY=$(cat "$SSH_KEY_INPUT")
        log_info "파일에서 SSH 키를 읽었습니다: $SSH_KEY_INPUT"
    else
        SSH_KEY="$SSH_KEY_INPUT"
    fi

    # SSH 키 형식 검증 (간단한 체크)
    if [[ ! "$SSH_KEY" =~ ^(ssh-rsa|ssh-ed25519|ssh-dss|ecdsa-sha2-) ]]; then
        log_warning "SSH 키 형식이 올바르지 않을 수 있습니다."
        echo -n "계속하시겠습니까? [y/N]: "
        read -r continue_anyway
        if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    pulumi config set --secret ssh_public_key "$SSH_KEY"
    log_success "SSH 키 설정 완료"
    echo ""
}

# 일반 설정
setup_general_config() {
    log_info "일반 설정을 구성합니다..."
    echo ""

    # 리전 설정
    echo "사용 가능한 OCI 리전:"
    echo "  - ap-osaka-1 (아시아 태평양 - 오사카)"
    echo "  - ap-seoul-1 (아시아 태평양 - 서울)"
    echo "  - ap-tokyo-1 (아시아 태평양 - 도쿄)"
    echo "  - us-ashburn-1 (미국 동부 - 애슈번)"
    echo "  - us-phoenix-1 (미국 서부 - 피닉스)"
    echo ""
    echo -n "리전 입력 [ap-osaka-1]: "
    read -r REGION
    REGION=${REGION:-ap-osaka-1}
    pulumi config set region "$REGION"
    log_success "리전 설정: $REGION"

    # OCI 프로필 설정
    echo ""
    echo -n "OCI CLI 프로필 이름 입력 [DEFAULT]: "
    read -r PROFILE
    PROFILE=${PROFILE:-DEFAULT}
    pulumi config set profile "$PROFILE"
    log_success "프로필 설정: $PROFILE"
    echo ""
}

# 설정 확인
verify_config() {
    log_info "설정 내용을 확인합니다..."
    echo ""

    echo -e "${CYAN}📋 현재 Pulumi 설정:${NC}"
    echo "   🏗️  스택: $(pulumi stack --show-name)"
    echo "   🔒 구획 ID: [암호화됨]"
    echo "   🔑 SSH 키: [암호화됨]"
    echo "   🌏 리전: $(pulumi config get region)"
    echo "   👤 프로필: $(pulumi config get profile)"
    echo ""

    # 설정 파일 존재 확인
    if [ -f "config.py" ]; then
        log_info "config.py 파일이 발견되었습니다."
        echo "   ✅ Python에서 이 설정들을 사용할 수 있습니다."
    else
        log_warning "config.py 파일이 없습니다."
        echo "   💡 config.py 파일을 생성하여 Python에서 설정을 사용하세요."
    fi
    echo ""
}

# 추가 도움말
show_next_steps() {
    echo -e "${CYAN}🚀 다음 단계:${NC}"
    echo "1. 인프라 배포: ${GREEN}pulumi up${NC}"
    echo "2. 설정 확인: ${GREEN}pulumi config${NC}"
    echo "3. 스택 목록: ${GREEN}pulumi stack ls${NC}"
    echo "4. 리소스 확인: ${GREEN}pulumi stack output${NC}"
    echo ""
    echo -e "${YELLOW}💡 유용한 명령어:${NC}"
    echo "   - pulumi config set <key> <value>     # 설정 추가/수정"
    echo "   - pulumi config get <key>             # 설정 조회"
    echo "   - pulumi config rm <key>              # 설정 삭제"
    echo "   - pulumi stack select <stack-name>    # 스택 전환"
    echo ""
}

# 메인 실행
main() {
    setup_stack
    setup_secrets
    setup_general_config
    verify_config
    log_success "모든 설정이 완료되었습니다!"
    echo ""
    show_next_steps
}

# 오류 처리
trap 'log_error "스크립트 실행 중 오류가 발생했습니다."; exit 1' ERR

# 스크립트 실행
main
