# agent-skills

Codex에서 사용하는 독립적인 지침형 스킬 모음입니다. 실행 스크립트나 다른 스킬에 의존하지 않으며, 각 스킬만 따로 설치할 수 있습니다.

| 스킬 | 목적과 사용 상황 |
| --- | --- |
| [wiki-capture](wiki-capture/SKILL.md) | 재사용할 결정·교훈·진행 상태를 평가하고 기존 Wiki 정책에 맞는 변경안을 준비합니다. |
| [reverse-engineering](reverse-engineering/SKILL.md) | 기존 코드의 구조·실행 흐름과 Git 이력의 설계 배경을 근거로 복원합니다. |
| [backend-architecture-review](backend-architecture-review/SKILL.md) | Java/Spring 중심의 설계안·기존 아키텍처를 요구사항, 대안, 트레이드오프로 검토합니다. |
| [tech-article-curation](tech-article-curation/SKILL.md) | 기술 원문을 분석해 기존 Obsidian 템플릿·태그에 맞는 학습 문서를 준비합니다. |

## 설치와 호출

[공식 OpenAI 설치 위치](https://learn.chatgpt.com/docs/build-skills)에 따라 **스킬 폴더 전체**를 아래 중 한 위치에 복사합니다. `SKILL.md`만 공통 디렉터리에 모으지 않습니다.

| 범위 | Codex App의 로컬 프로젝트에서 사용하는 경로 |
| --- | --- |
| 사용자 공통 | `$HOME/.agents/skills/<skill-name>/SKILL.md` |
| 프로젝트별 | `<project>/.agents/skills/<skill-name>/SKILL.md` |

Windows PowerShell의 `$HOME`은 사용자 홈입니다. 예를 들어 이 저장소 루트에서 한 스킬을 사용자 공통으로 설치하려면:

```powershell
$skillName = 'wiki-capture'
$skillDestination = Join-Path $HOME ".agents/skills/$skillName"
if (Test-Path -LiteralPath $skillDestination) { throw '기존 설치를 먼저 확인하세요.' }
New-Item -ItemType Directory -Force (Split-Path $skillDestination) | Out-Null
Copy-Item -LiteralPath "./$skillName" -Destination $skillDestination -Recurse
```

프로젝트별 설치는 대상 경로를 `<project>/.agents/skills`로 바꿉니다. 저장소 루트의 네 폴더는 배포 원본이므로, 저장소를 clone하는 것만으로 자동 설치되지는 않습니다. 설치 위치가 중복되면 같은 이름이 여러 개 보일 수 있습니다. 변경이 보이지 않으면 Codex를 재시작하고 해당 프로젝트의 스킬 목록을 확인합니다.

```text
$wiki-capture 이번 작업의 확정 결정과 검증 한계를 평가해 초안을 준비해 줘.
$reverse-engineering 주문 생성 요청부터 DB까지 코드와 이력으로 복원해 줘.
$backend-architecture-review 이 설계의 동시성·트랜잭션 경계를 검토해 줘.
$tech-article-curation 이 원문을 읽고 기존 템플릿의 학습 문서를 준비해 줘.
```

## 권한과 검증 범위

구조 복원과 설계 리뷰는 읽기 전용입니다. Wiki·기술 글 스킬도 분석·초안 준비만으로 외부 게시 권한을 얻지 않습니다. GitHub 연결의 읽기/쓰기 권한과 사용자의 게시 승인은 별개이며, 권한이 없으면 보류 초안을 반환합니다. Wiki는 검토 PR까지만 수행하고 병합하지 않습니다. 기술 글 저장은 승인된 경우에만 기존 `daily-tech`·CI 계약을 따르며 스케줄러를 변경하지 않습니다.

형식 검사·실제 코드/원문 사례 검토·격리 아카이브 검사 결과와 제한은 [병합 전 검증 기록](tests/pre-merge-validation.md)에 정리합니다. 원격 Wiki/아카이브 게시, 실제 운영 장애 재현, Obsidian GUI·이미지 표시, 모든 클라이언트의 자동 선택은 보장하지 않습니다. 과거 사례 기록은 현재 HEAD 검증과 구분합니다.

## CI와 병합 준비

PR 및 `dev` push에서 `Skill validation` 워크플로가 공식 `skills-ref`와 기본 Markdown 구조 검사를 실행합니다. 공식 검증기의 의존성은 CI 도구에만 설치하며 스킬 런타임 의존성은 추가하지 않습니다.

```text
skills-ref validate wiki-capture
skills-ref validate reverse-engineering
skills-ref validate backend-architecture-review
skills-ref validate tech-article-curation
python scripts/check_markdown.py
```

Markdown 검사는 H1·frontmatter/코드 fence 닫힘·로컬 링크를 확인합니다. Mermaid 구문/화면 렌더링이나 문서의 사실성을 대신 검증하지 않습니다. `main`에는 PR과 필수 `Validate skills and Markdown` 검사를 요구하도록 보호 설정을 사용합니다. 현재 적용 상태는 검증 기록에서 확인합니다. 이 작업은 PR 생성이나 `main` 병합을 수행하지 않습니다.

## ChatGPT / Codex 플러그인 패키지

기존 네 `SKILL.md`는 원본으로 유지하며, [플러그인 카탈로그](.agents/plugins/marketplace.json)에 각 스킬을
**독립적인 Skills-only 플러그인**으로 패키징했습니다. 별도 MCP 서버, 스크립트 실행
후크, 자격 증명은 없습니다. [카탈로그](.agents/plugins/marketplace.json)는
한 번에 네 개의 플러그인을 선택·설치할 수 있게 노출합니다.

| 플러그인 | 배포 패키지 |
| --- | --- |
| Wiki Capture | [plugins/wiki-capture](plugins/wiki-capture/plugin.json) |
| Reverse Engineering | [plugins/reverse-engineering](plugins/reverse-engineering/plugin.json) |
| Backend Architecture Review | [plugins/backend-architecture-review](plugins/backend-architecture-review/plugin.json) |
| Tech Article Curation | [plugins/tech-article-curation](plugins/tech-article-curation/plugin.json) |

### GitHub 마켓플레이스 등록 및 개인 설치

[공식 설치 문서](https://developers.openai.com/plugins/build/plugins) 기준,
지원되는 Codex CLI에서 다음 명령으로 저장소의 플러그인 카탈로그를 추가합니다.
이 저장소의 `main`에 패키징 변경이 병합된 이후에는:

```powershell
codex plugin marketplace add guseoh/agent-skills --ref main
codex plugin marketplace list
```

병합 전 별도 개발 브랜치에서 검토하려면 `--ref feat/package-four-skills-plugins`을
지정할 수 있습니다. 이후 Codex의 `/plugins` 또는 ChatGPT **데스크톱 앱**의
Plugins Directory에서 `Guseoh Agent Skills` 소스를 선택하고 네 플러그인을
**각각 설치**한 다음 새 채팅에서 작동을 확인합니다. 명시적 호출은
`$wiki-capture`처럼 기존 스킬명을 사용하고, 실제 UI의 멘션 표기는 설치 환경을
확인합니다. 저장소를 Push하는 것만으로 사용자 계정에 자동 설치되지는 않습니다.

소스 수정 후:
```powershell
python scripts/package_plugins.py --sync
python scripts/package_plugins.py --check
```

CI는 원본과 배포본의 일치 및 양쪽 스킬 형식을 검증합니다.
기존 `$HOME/.agents/skills/`에 수동 설치된 같은 이름의 스킬은
중복 표시될 수 있으므로 변경 전에 설치 상태를 확인하세요.

### ChatGPT 웹 / 공개 플러그인 디렉터리

이 카탈로그는 로컬·GitHub 마켓플레이스 기반 **개발/개인 사용 등록**입니다.
ChatGPT 웹의 플러그인 디렉터리에 자동으로 게시되지 않습니다.
공개 디렉터리에 등록할 경우 각 `plugins/<name>/`을 개별 ZIP으로 묶고
[공식 제출·검토 절차](https://developers.openai.com/plugins/deploy/submission)의
개발자 인증, 업로드, 검증 및 별도 공개 승인을 거쳐야 합니다.
웹 설치·클라이언트 자동 선택은 이번 GitHub 변경만으로 검증할 수 없습니다.

ZIP 업로드가 지원되는 계정·워크스페이스라면 저장소를 로컬에 가져온 뒤
각 패키지의 **내용물**을 ZIP 루트에 넣어 네 개의 독립 파일로 만들 수 있습니다.

```powershell
New-Item -ItemType Directory -Force dist | Out-Null
foreach ($name in @('wiki-capture','reverse-engineering','backend-architecture-review','tech-article-curation')) {
  Compress-Archive -Path "./plugins/$name/*" -DestinationPath "./dist/$name-0.1.0.zip" -Force
}
```

공개 플러그인 제출은 계정의 개발자 제출 권한과 검토 절차가 필요합니다.
ChatGPT 웹에서 개인용 등록·설치가 지원되는지 확인하기 전에는 ZIP 생성만으로
설치 완료나 공개 등록을 주장하지 않습니다.
특히 기존 Wiki/Obsidian에 쓰는 권한은 설치 자체가 승인하지 않습니다.
