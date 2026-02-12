# Gemini MCP Agent

Gemini SDK로 MCP 서버에 연결하여 도구를 호출하는 코딩 에이전트.

## 환경 설정

### 1. 사전 요구사항

- Python 3.12 이상
- [uv](https://docs.astral.sh/uv/) 설치

```bash
# uv 설치 (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 의존성 설치

```bash
uv sync
```

이 명령어가 자동으로:

- `.venv` 가상환경 생성
- `google-genai`, `mcp` 패키지 설치

> OneDrive 폴더에서 하드링크 오류가 발생하면:
>
> ```bash
> uv sync --link-mode=copy
> ```

### 3. Gemini API 키 설정

`agent.py`의 `__init__`에서 API 키를 직접 설정하거나, 환경변수를 사용:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key"

# Linux/Mac
export GEMINI_API_KEY="your-api-key"
```

API 키는 [Google AI Studio](https://aistudio.google.com/apikey)에서 발급.

### 4. MCP 서버 설정

`config.json`에 사용할 MCP 서버를 정의:

```json
{
  "mcpServers": {
    "mcp-devdiary": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/JaehaSS/mcp-devdiary.git",
        "mcp-devdiary"
      ],
      "env": {
        "GITHUB_TOKEN": "Github_TOKEN",
        "GITHUB_USERNAME": "GITHUB_USER_NAME"
      }
    }
  }
}
```

여러 MCP 서버를 동시에 연결할 수 있다.

## 실행

```bash
uv run python main.py
```

config 파일 경로를 지정하려면:

```bash
uv run python main.py path/to/config.json
```

실행하면 대화형 프롬프트가 나타난다:

```
[연결됨] mcp-devdiary: ['get_commits', 'get_weekly_activity', 'get_activity_for_resume', ...]

=== Gemini MCP Agent ===
종료하려면 'quit' 또는 'exit'를 입력하세요.

You:
```

종료: `quit`, `exit`, 또는 `Ctrl+C`

## 사용 예시 (mcp-devdiary)

### 연결되는 MCP 도구 목록

[mcp-devdiary](https://github.com/JaehaSS/mcp-devdiary)가 제공하는 7개 도구가 자동으로 Gemini에 등록된다:

| Tool | Description |
|------|-------------|
| `get_commits` | GitHub 주간 커밋 내역 및 통계 조회 |
| `get_weekly_activity` | 커밋 + PR + 에이전트 세션 통합 주간 활동 |
| `get_activity_for_resume` | 이력서용 다주간 활동 데이터 |
| `get_agent_sessions` | Claude Code / Codex 세션 히스토리 |
| `get_weekly_timeline` | 전체 활동의 시간순 타임라인 |
| `get_enriched_weekly_report` | Few-shot 예제 포함 주간 리포트 |
| `get_weekly_insights` | 패턴 분석 및 개선 제안 |

### get_commits 예제

이번 주 커밋 내역을 가져오는 예시:

```
You: 이번 주 내 커밋 내역을 알려줘
  [도구 호출] get_commits({"username": "Jjaeha", "week_offset": 0})

Gemini: 이번 주(2026-02-09 ~ 2026-02-15) 커밋 내역입니다:

  - feat: MCP 에이전트 초기 구현 (agent.py, main.py)
  - docs: README 작성
  - fix: OneDrive 하드링크 오류 해결

  총 3개 커밋, 5개 파일 변경
```

지난 주 커밋을 보려면:

```
You: 지난 주 커밋 보여줘
  [도구 호출] get_commits({"username": "Jjaeha", "week_offset": -1})

Gemini: 지난 주(2026-02-02 ~ 2026-02-08) 커밋 내역입니다: ...
```

### 기타 질문 예시

```
You: 이번 주 작업 요약해줘
  [도구 호출] get_enriched_weekly_report({"username": "Jjaeha", "week_offset": 0})
```

```
You: 최근 한 달 활동으로 이력서 항목 만들어줘
  [도구 호출] get_activity_for_resume({"username": "Jjaeha", "weeks_range": 4})
```

```
You: 내 코딩 패턴 분석해줘
  [도구 호출] get_weekly_insights({"username": "Jjaeha", "week_offset": 0})
```

## 프로젝트 구조

```
├── agent.py         # Gemini + MCP 브릿지 에이전트 (핵심 로직)
├── main.py          # CLI 진입점
├── config.json      # MCP 서버 설정
├── pyproject.toml   # uv 프로젝트 설정
└── requirements.txt # pip용 의존성 목록
```

## 동작 흐름

1. `config.json`의 MCP 서버를 `uvx`로 실행하여 stdio 연결
2. MCP 서버의 도구 목록을 Gemini `FunctionDeclaration`으로 변환
3. 사용자 쿼리를 Gemini에 전송
4. Gemini가 도구 호출을 요청하면 MCP를 통해 실행
5. 결과를 다시 Gemini에 전달하여 최종 응답 생성
6. 도구 호출이 더 이상 없을 때까지 반복 (최대 10회)
