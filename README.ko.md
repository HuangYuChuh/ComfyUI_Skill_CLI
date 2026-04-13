<div align="center">

> **이 문서는 AI에 의해 번역되었습니다. 기여를 환영합니다!** · 원본: [`README.md`](./README.md) @ `72e6a63`

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>ComfyUI 워크플로우 스킬을 관리하고 실행하기 위한 에이전트 친화적 커맨드라인 도구.</strong></p>

  <p>
    셸 명령을 실행할 수 있는 모든 AI 에이전트(Claude Code, Codex, OpenClaw 등)는 이 CLI를 통해 ComfyUI를 사용할 수 있습니다.
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#install">설치</a> ·
    <a href="#quick-start">빠른 시작</a> ·
    <a href="#commands">명령어</a> ·
    <a href="#for-ai-agents">AI 에이전트용</a>
  </p>

  <p>
    <a href="./README.md">English</a> ·
    <a href="./README.zh.md">简体中文</a> ·
    <a href="./README.zh-TW.md">繁體中文</a> ·
    <a href="./README.ja.md">日本語</a> ·
    <strong>한국어</strong> ·
    <a href="./README.es.md">Español</a>
  </p>

</div>

---

## comfyui-skill이 필요한 이유

| 기능 | 의미 |
|------|------|
| **에이전트 네이티브** | 구조화된 JSON 출력, 파이프 친화적, AI 에이전트 호출을 위해 설계됨 |
| **설정 불필요** | 현재 디렉터리의 `config.json` 및 `data/`를 자동으로 읽음, 별도 설정 없음 |
| **전체 생명주기** | 워크플로우 및 의존성의 탐색, 가져오기, 실행, 취소, 관리를 하나의 도구에서 |
| **멀티 서버** | 여러 ComfyUI 인스턴스 관리, 다른 하드웨어로 작업 라우팅 |
| **모델 탐색** | 대상 서버에서 직접 모델 폴더 및 사용 가능한 모델 이름 확인 |
| **워크플로우 플릿 관리** | 여러 머신에 걸쳐 워크플로우 가져오기, 활성화, 비활성화, 삭제 및 마이그레이션 |
| **오류 안내** | 일반적인 오류(OOM, 인증 실패, 모델 누락)에 대한 실행 가능한 힌트 반환 |

<a id="install"></a>
## 설치

```bash
pipx install comfyui-skill-cli
```

또는 pip으로:

```bash
pip install comfyui-skill-cli
```

### 업데이트

```bash
pipx upgrade comfyui-skill-cli
```

### 개발 모드

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

<a id="quick-start"></a>
## 빠른 시작

```bash
# 1. ComfyUI Skills 프로젝트 디렉터리로 이동
cd /path/to/your-skills-project

# 2. 서버 상태 확인
comfyui-skill server status

# 3. 사용 가능한 워크플로우 목록 조회
comfyui-skill list

# 4. 워크플로우 실행
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

모든 명령은 구조화된 출력을 위해 `--json`을 지원합니다.

## ID 규칙

워크플로우는 `<server_id>/<workflow_id>` 형식으로 지정합니다:

```bash
comfyui-skill run local/txt2img          # 명시적 서버 지정
comfyui-skill run txt2img                # 기본 서버 사용
comfyui-skill run txt2img -s my_server   # --server 플래그로 재정의
```

<a id="commands"></a>
## 명령어

### 워크플로우 탐색 및 실행

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill list` | 파라미터와 함께 모든 사용 가능한 워크플로우 목록 조회 |
| `comfyui-skill info <id>` | 워크플로우 상세 정보 및 파라미터 스키마 표시 |
| `comfyui-skill run <id> --args '{...}'` | 워크플로우 실행 (블로킹, 실시간 WebSocket 스트리밍) |
| `comfyui-skill run <id> --validate` | 실행 없이 워크플로우 유효성 검사 |
| `comfyui-skill submit <id> --args '{...}'` | 워크플로우 제출 (논블로킹) |
| `comfyui-skill status <prompt_id>` | 실행 상태 확인 및 발견된 결과 표시 |
| `comfyui-skill cancel <prompt_id>` | 실행 중이거나 대기 중인 작업 취소 |
| `comfyui-skill upload <file>` | 워크플로우에서 사용할 파일을 ComfyUI에 업로드 |
| `comfyui-skill upload <file> --mask` | 인페인팅 워크플로우용 마스크 이미지 업로드 |
| `comfyui-skill upload --from-output <prompt_id>` | 이전 실행 결과를 다음 워크플로우의 입력으로 연결 |

### 큐 및 리소스 관리

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill queue list` | 실행 중 및 대기 중인 작업 표시 |
| `comfyui-skill queue clear` | 모든 대기 중인 작업 지우기 |
| `comfyui-skill queue delete <prompt_id>...` | 큐에서 특정 작업 제거 |
| `comfyui-skill free` | GPU 메모리 해제 및 모델 언로드 |
| `comfyui-skill free --models` | 모델만 언로드 |
| `comfyui-skill free --memory` | 캐시된 메모리만 해제 |

### 노드 및 모델 탐색

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill nodes list` | 카테고리별 모든 사용 가능한 ComfyUI 노드 목록 조회 |
| `comfyui-skill nodes info <class>` | 노드 입출력 스키마 표시 |
| `comfyui-skill nodes search <query>` | 이름 또는 카테고리로 노드 검색 |
| `comfyui-skill models list` | 모든 사용 가능한 모델 폴더 목록 조회 |
| `comfyui-skill models list <folder>` | 특정 폴더의 모델 목록 조회 (예: `checkpoints`, `loras`) |

### 워크플로우 관리

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill workflow import <path>` | 워크플로우 가져오기 (포맷 자동 감지, 스키마 자동 생성) |
| `comfyui-skill workflow import --from-server` | ComfyUI 서버 userdata에서 하나 이상의 워크플로우 가져오기 |
| `comfyui-skill workflow enable <id>` | 워크플로우 활성화 |
| `comfyui-skill workflow disable <id>` | 워크플로우 비활성화 |
| `comfyui-skill workflow delete <id>` | 워크플로우 삭제 |

### 서버 관리

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill server list` | 설정된 모든 서버 목록 조회 |
| `comfyui-skill server status` | ComfyUI 서버 온라인 상태 확인 |
| `comfyui-skill server stats` | VRAM, RAM, GPU 정보 표시 (멀티 서버의 경우 `--all`) |
| `comfyui-skill server add --id <id> --url <url>` | 새 서버 추가 |
| `comfyui-skill server enable/disable <id>` | 서버 가용성 토글 |
| `comfyui-skill server remove <id>` | 서버 제거 |

### 의존성 관리

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill deps check <id>` | 누락된 커스텀 노드 및 모델 확인 |
| `comfyui-skill deps install <id> --all` | 누락된 모든 의존성 자동 감지 및 설치 |
| `comfyui-skill deps install <id> --repos '[...]'` | 특정 커스텀 노드 설치 |
| `comfyui-skill deps install <id> --models` | Manager를 통해 누락된 모델 설치 |

### 설정 및 기록

| 명령어 | 설명 |
|--------|------|
| `comfyui-skill config export --output <path>` | 설정 및 워크플로우를 번들로 내보내기 |
| `comfyui-skill config import <path>` | 설정 번들 가져오기 (`--dry-run` 지원) |
| `comfyui-skill history list <id>` | 실행 기록 목록 조회 |
| `comfyui-skill history show <id> <run_id>` | 특정 실행의 상세 정보 표시 |
| `comfyui-skill jobs list` | 서버 측 작업 기록 목록 조회 (`--status`로 필터링) |
| `comfyui-skill jobs show <prompt_id>` | 특정 작업의 상세 정보 표시 |
| `comfyui-skill logs show` | 최근 ComfyUI 서버 로그 표시 |
| `comfyui-skill templates list` | 커스텀 노드의 워크플로우 템플릿 목록 조회 |
| `comfyui-skill templates subgraphs` | 재사용 가능한 서브그래프 컴포넌트 목록 조회 |

### 전역 옵션

| 옵션 | 설명 |
|------|------|
| `--json, -j` | JSON 출력 강제 |
| `--output-format` | 출력 형식: `text`, `json`, `stream-json` |
| `--server, -s` | 서버 ID 지정 |
| `--dir, -d` | 데이터 디렉터리 지정 (기본값: 현재 디렉터리) |
| `--verbose, -v` | 상세 출력 |
| `--no-update-check` | 자동 CLI 업데이트 확인 건너뜀 |

### 출력 모드

| 모드 | 조건 | 형식 |
|------|------|------|
| 텍스트 | TTY 터미널 | 리치 테이블 및 진행 표시줄 |
| JSON | 파이프 또는 `--json` | 단일 JSON 결과 |
| 스트림 JSON | `--output-format stream-json` | 실시간 NDJSON 이벤트 |
| 오류 | 항상 | stderr |

## 일반적인 관리 작업

### 서버의 모델 확인

```bash
comfyui-skill models list
comfyui-skill models list checkpoints
comfyui-skill models list loras
```

워크플로우나 스키마에 모델을 연결하기 전에 모델 이름을 확인할 때 사용하세요.

### 여러 워크플로우 관리

```bash
# ComfyUI 서버 userdata에서 사용 가능한 워크플로우 미리보기
comfyui-skill workflow import --from-server --preview

# 서버에서 이름이 일치하는 워크플로우 가져오기
comfyui-skill workflow import --from-server --name sdxl

# 워크플로우 일시적으로 비활성화 또는 재활성화
comfyui-skill workflow disable local/old-flow
comfyui-skill workflow enable local/old-flow

# 더 이상 노출하고 싶지 않은 워크플로우 제거
comfyui-skill workflow delete local/old-flow
```

### 머신 간 워크플로우 번들 이동

```bash
comfyui-skill config export --output ./bundle.json --portable-only
comfyui-skill config import ./bundle.json --dry-run
comfyui-skill config import ./bundle.json --apply-environment
```

여러 워크플로우를 한꺼번에 마이그레이션하고 싶을 때, 수동으로 다시 가져오는 대신 이 방법을 사용하세요.

### 실행 전 모델 및 의존성 확인

```bash
comfyui-skill deps check local/txt2img
comfyui-skill deps install local/txt2img --models
comfyui-skill deps install local/txt2img --all
```

<a id="for-ai-agents"></a>
## AI 에이전트용

이 CLI는 `SKILL.md` 정의에서 호출되도록 설계되었습니다. 일반적인 에이전트 워크플로우:

```bash
comfyui-skill server status --json                    # 1. 서버 확인
comfyui-skill list --json                             # 2. 워크플로우 탐색
comfyui-skill info local/txt2img --json               # 3. 파라미터 확인
comfyui-skill run local/txt2img --args '{...}' --json # 4. 실행
```

### 워크플로우 체이닝 (다단계 파이프라인)

```bash
# 첫 번째 워크플로우 실행
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# 결과를 다음 워크플로우에 연결
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### 가져오기 및 유효성 검사

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## 기여하기

기여를 환영합니다! 설계 원칙 및 PR 워크플로우에 대해서는 메인 저장소의 [기여 가이드](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md)를 참고하세요.

## 리소스

- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — 메인 스킬 저장소
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — 이 CLI가 오케스트레이션하는 백엔드
- [Typer](https://typer.tiangolo.com/) — 이 프로젝트에서 사용하는 CLI 프레임워크

[Typer](https://typer.tiangolo.com/)로 구축되었으며, [comfy-cli](https://github.com/Comfy-Org/comfy-cli)와 동일한 프레임워크를 사용합니다. 향후 `comfy skills` 서브커맨드로 통합될 예정입니다.
