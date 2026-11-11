# agent-skills

Codex에서 사용하는 독립적인 지침형 스킬 모음입니다. 각 스킬은 따로 설치할 수 있으며 다른 스킬에 의존하지 않습니다. 시각화 스킬에는 선택적으로 실행하는 Python 표준 라이브러리 기반 SVG 검사기가 포함됩니다. 자동 실행 후크는 없습니다.

| 스킬 | 목적과 사용 상황 |
| --- | --- |
| [wiki-capture](wiki-capture/SKILL.md) | 재사용할 결정·교훈·진행 상태를 평가하고 기존 Wiki 정책에 맞는 변경안을 준비합니다. |
| [reverse-engineering](reverse-engineering/SKILL.md) | 프로젝트를 취준생 눈높이로 해체 분석하고 설계 이유·트레이드오프·포트폴리오 핵심 주제를 근거로 심화합니다. |
| [backend-architecture-review](backend-architecture-review/SKILL.md) | Java/Spring 중심의 설계안·기존 아키텍처를 요구사항, 대안, 트레이드오프로 검토합니다. |
| [tech-article-curation](tech-article-curation/SKILL.md) | 기술 원문을 분석해 기존 Obsidian 템플릿·태그에 맞는 학습 문서를 준비합니다. |
| [cs-learning-visualization](cs-learning-visualization/SKILL.md) | CS 개념을 SVG 중심으로 시각화하고 의미·임의 SVG 형식·대상 환경 표시를 검수합니다. 복사 요청에는 PNG를 함께 제공합니다. |
| [concept-learning](concept-learning/SKILL.md) | 기존 개념 학습 교수법으로 Java·Spring·JPA·DB·Linux·시스템 설계 등을 한국어로 설명합니다. |

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

프로젝트별 설치는 대상 경로를 `<project>/.agents/skills`로 바꿉니다. 저장소 루트의 각 스킬 폴더는 배포 원본이므로, 저장소를 clone하는 것만으로 자동 설치되지는 않습니다. 설치 위치가 중복되면 같은 이름이 여러 개 보일 수 있습니다. 변경이 보이지 않으면 Codex를 재시작하고 해당 프로젝트의 스킬 목록을 확인합니다.

```text
$wiki-capture 이번 작업의 확정 결정과 검증 한계를 평가해 초안을 준비해 줘.
$reverse-engineering 주문 생성 요청부터 DB까지 코드와 이력으로 복원해 줘.
$backend-architecture-review 이 설계의 동시성·트랜잭션 경계를 검토해 줘.
$tech-article-curation 이 원문을 읽고 기존 템플릿의 학습 문서를 준비해 줘.
$cs-learning-visualization Heap의 트리·배열 구조를 검증 가능한 SVG로 그려줘.
$concept-learning 다형성1부터 진행하자.
$concept-learning Spring의 Bean 생명주기 설명해줘.
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
skills-ref validate cs-learning-visualization
skills-ref validate concept-learning
python scripts/test_concept_learning.py
python scripts/check_markdown.py
python scripts/check_learning_visuals.py
python scripts/test_svg_validator.py
```

Markdown 검사는 H1·frontmatter/코드 fence 닫힘·로컬 링크를 확인합니다. Mermaid 구문/화면 렌더링이나 문서의 사실성을 대신 검증하지 않습니다. `main`에는 PR과 필수 `Validate skills and Markdown` 검사를 요구하도록 보호 설정을 사용합니다. 현재 적용 상태는 검증 기록에서 확인합니다. 이 작업은 PR 생성이나 `main` 병합을 수행하지 않습니다.

## ChatGPT / Codex 플러그인 패키지

기존 스킬의 `SKILL.md`는 원본으로 유지하며, [플러그인 카탈로그](.agents/plugins/marketplace.json)에 각 스킬을
**독립적인 Skills-only 플러그인**으로 패키징했습니다. 별도 MCP 서버, 스크립트 실행
후크, 자격 증명은 없습니다. [카탈로그](.agents/plugins/marketplace.json)는
한 번에 여섯 개의 플러그인을 선택·설치할 수 있게 노출합니다.

| 플러그인 | 배포 패키지 |
| --- | --- |
| Wiki Capture | [plugins/wiki-capture](plugins/wiki-capture/plugin.json) |
| Reverse Engineering | [plugins/reverse-engineering](plugins/reverse-engineering/plugin.json) |
| Backend Architecture Review | [plugins/backend-architecture-review](plugins/backend-architecture-review/plugin.json) |
| Tech Article Curation | [plugins/tech-article-curation](plugins/tech-article-curation/plugin.json) |
| CS Learning Visualization | [plugins/cs-learning-visualization](plugins/cs-learning-visualization/plugin.json) |
| Concept Learning | [plugins/concept-learning](plugins/concept-learning/plugin.json) |

### GitHub 마켓플레이스 등록 및 개인 설치

[공식 설치 문서](https://developers.openai.com/plugins/build/plugins) 기준,
지원되는 Codex CLI에서 다음 명령으로 저장소의 플러그인 카탈로그를 추가합니다.
이 저장소의 `main`에 패키징 변경이 병합된 이후에는:

```powershell
codex plugin marketplace add guseoh/agent-skills --ref main
codex plugin marketplace list
```

병합 전 별도 개발 브랜치에서 검토하려면 `--ref <검증할-브랜치명>`을
지정할 수 있습니다. 이후 Codex의 `/plugins` 또는 ChatGPT **데스크톱 앱**의
Plugins Directory에서 `Guseoh Agent Skills` 소스를 선택하고 여섯 플러그인을
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

### CS 학습 시각화 파일과 검증

[세 가지 SVG 예제 갤러리](cs-learning-visualization/examples/index.html)와 [품질 검증 기준](tests/learning-visualization.md)을 포함합니다. 스킬 패키지에도 SVG 및 갤러리가 함께 들어갑니다. Heap은 트리·배열 인덱스, Java는 참조값 복사, TCP는 바이트 단위 누적 ACK를 검증합니다. `python scripts/check_learning_visuals.py`는 SVG 형식·명시적 샘플 상태를 자동 검사하지만, 실제 브라우저 육안 검증과 최신 Reader 통합을 대체하지 않습니다. 그림 원본은 외부 프로젝트에서 복사하지 않고 새로 제작했습니다.

### 개념 학습 전용 플러그인

[Concept Learning](concept-learning/SKILL.md)은 **Java/Spring 백엔드 신입~2년 차 수준**의 기술 강사 스킬입니다. 기존 로드맵에서 `다형성1 진행하자`라고 요청하거나 독립적으로 `Bean 생명주기 설명해줘`라고 하더라도 **같은 설명 규칙**을 적용하며 로드맵 설계·진도 관리에는 관여하지 않습니다.

- **깊이:** 기본 문법 소개를 반복하지 않고 실제 코드의 동작, 객체 책임 배치, 실행/설계 판단 기준, 한계와 트레이드오프를 충분히 설명합니다. 장문 자체가 목표는 아니며 문단·글머리표·표를 내용에 따라 사용합니다.
- **소제목별 참고 자료:** 각 **실질적인 주요 소제목과 핵심 하위 주제**에 적합한 한국어 기술 글을 실제 탐색하고, 읽은 핵심 내용과 링크를 가까운 문단에 반영합니다. 개인 개발 블로그(Tistory·Velog·Medium·GitHub.io 등), **테코블(Tecoble)**, 한국 IT 기업 기술 블로그를 적극 고려하며 한빛미디어·위키독스 추천은 제외합니다.
- **실제 이미지:** 구조·상태·호출 흐름에 도움이 될 때 원본 기술 글·강의의 실제 개념 이미지를 우선 확인해 사용합니다. 출처·권한·실제 표시 여부를 확인하고 **파비콘·로고·빈 이미지 자리**를 이미지로 취급하지 않습니다. 도식은 보조 수단입니다.
- **설명/정리 모드:** [요청 모드 규칙](concept-learning/references/response-modes.md)에 따라 `설명해줘`·`진행하자`는 원리·실행·설계 판단까지 깊게 설명하고, `정리해줘`·`요약해줘`는 **핵심 개념·구분·주의점만 간결하게 요약**합니다. 정확성·출처 검증·보안은 공통이며 조사 규모·코드·이미지의 사용량은 목적에 맞춥니다.
- **작성 전 조사(Research First):** [조사 우선 워크플로](concept-learning/references/research-first-workflow.md)에 따라 **요청 모드 확인 → 주제 분석 → 관련 한국어 기술 블로그·필요한 서적의 공개 목차/해설·도움되는 실제 내용 이미지 선조사 → 근거 지도 → 모드별 작성** 순서로 진행합니다. 예를 들어 **다형성**에서는 《오브젝트》와 《객체지향의 사실과 오해》를 관련성 검토 후 공개 기술 해설의 탐색 키워드로 활용하지만, **Spring Bean 생명주기처럼 관련 없는 주제에는 해당 책을 끌어오지 않습니다.** 읽지 않은 책의 본문을 읽었다고 주장하지 않습니다.
- **국문 기술 글·글로벌 이미지 검색 (v0.6.1):** 본문의 핵심 해설·사례에 인용하는 기술 글은 **한국어 개인·국내 IT 기업 기술 블로그를 대부분으로**, 기술 사실은 언어와 관계없이 공식 레퍼런스로 검증합니다. 학습 이미지 검색은 **한국어·영어 및 해외 공식 문서·기술 블로그·강의 자료까지 확장**하고 원본 적합성·글자 가독성·이용 조건을 검증한 뒤 영문 라벨을 한국어로 설명합니다. [자료/이미지 활용 규칙](concept-learning/references/source-and-visual-guidance.md)을 참조하세요.
- **EXPLAIN 추가 품질 점검 (v0.6.0):** [답변 품질 게이트](concept-learning/references/response-quality-gate.md)에서 **G2 출처가 소제목의 구체적 주장을 직접 설명하는지, G4 실제 개념 이미지가 링크/파비콘이 아닌 본문 미디어로 포함되고 코드와 연결되는지, G5 예제가 약속한 동작을 실제 호출하는지, G6 같은 말을 반복하지 않는지, G7 서적에서 확인한 관점이 본문에 적용되는지** 검토합니다. SUMMARIZE의 기존 간결한 구성은 유지합니다.
- **최종 자체 점검:** [답변 품질 게이트](concept-learning/references/response-quality-gate.md)의 **G0~G8**에 따라 초안 전에 근거 확보 여부를 확인하고, 완성 후 신입~2년 차 수준, 소제목별 출처, 실제 이미지, 코드 동작, 반복·가독성, 유익한 심화 키워드를 PASS / REVISE / LIMITATION으로 내부 점검합니다. 부족하면 **자료 탐색 단계로 돌아가 수정**합니다. 별도 모델 평가나 실행 후크가 아니므로 **CI 통과가 실제 답변 품질을 보증하지는 않습니다**.

세부 지침: [교수법 26개 규칙](concept-learning/references/teaching-rules.md),
[분야별 기준](concept-learning/references/subject-guidance.md),
[자료·이미지 활용](concept-learning/references/source-and-visual-guidance.md),
[주제 경계](concept-learning/references/topic-context.md),
[실패·합격 사례](concept-learning/references/quality-cases.md),
[프로젝트 연결](concept-learning/references/project-instructions.md).

### ChatGPT 웹 / 공개 플러그인 디렉터리

이 카탈로그는 로컬·GitHub 마켓플레이스 기반 **개발/개인 사용 등록**입니다.
ChatGPT 웹의 플러그인 디렉터리에 자동으로 게시되지 않습니다.
공개 디렉터리에 등록할 경우 각 `plugins/<name>/`을 개별 ZIP으로 묶고
[공식 제출·검토 절차](https://developers.openai.com/plugins/deploy/submission)의
개발자 인증, 업로드, 검증 및 별도 공개 승인을 거쳐야 합니다.
웹 설치·클라이언트 자동 선택은 이번 GitHub 변경만으로 검증할 수 없습니다.

ZIP 업로드가 지원되는 계정·워크스페이스라면 저장소를 로컬에 가져온 뒤
각 패키지의 **내용물**을 ZIP 루트에 넣어 여섯 개의 독립 ZIP 파일로 만들 수 있습니다.

```powershell
New-Item -ItemType Directory -Force dist | Out-Null
foreach ($name in @('wiki-capture','reverse-engineering','backend-architecture-review','tech-article-curation','cs-learning-visualization','concept-learning')) {
  Compress-Archive -Path "./plugins/$name/*" -DestinationPath "./dist/$name-0.1.0.zip" -Force
}
```

공개 플러그인 제출은 계정의 개발자 제출 권한과 검토 절차가 필요합니다.
ChatGPT 웹에서 개인용 등록·설치가 지원되는지 확인하기 전에는 ZIP 생성만으로
설치 완료나 공개 등록을 주장하지 않습니다.
특히 기존 Wiki/Obsidian에 쓰는 권한은 설치 자체가 승인하지 않습니다.

### 해체 분석·시각화 v0.2.0

Reverse Engineering은 전체 지도에서 실제 실행과 내부 원리로 내려가며, 기록된 설계 이유와 현재 분석한 대안을 구분합니다. 포트폴리오 후보는 기술 이름보다 문제·제약·트레이드오프·실측 근거로 선정합니다. 상세 기준은 스킬과 함께 배포됩니다.

CS Learning Visualization은 [품질·출력 기준](cs-learning-visualization/references/quality-and-delivery.md)과 [임의 SVG 검사기](cs-learning-visualization/scripts/validate_svg.py)를 포함합니다. 기본 한국어와 필요한 영어 용어를 사용하고, 본문 미리보기와 원본 SVG를 제공합니다. 공통 정적 검사·예제 의미 검사·렌더링·실제 사용 환경 검증은 별개입니다. [이번 변경 검증](tests/review-2026-11-11.md)을 참조하세요.

현재 카탈로그는 Codex/ChatGPT용입니다. 두 스킬의 공통 본문과 리소스를 Claude에서 재사용할 수 있는지와 Claude 플러그인 패키지 설치는 별도 확인 대상입니다. 이 변경은 Claude용 카탈로그·설치나 새 버전의 Codex/Claude 종단 호출을 검증했다고 주장하지 않습니다.
