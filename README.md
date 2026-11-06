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
