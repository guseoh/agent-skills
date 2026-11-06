# tech-article-curation 검증

검증일: 2026-11-07. 구현 기준: `dev`의 `d5003dc`. 기존 스킬·아카이브·스케줄러 설정은 변경하지 않았다.

## 원본 계약과 격리

`guseoh/cs`의 `main` SHA `b912934c8afd68baecd921f5e6dd883685be5013`을 임시 sparse 복제했다. 상위 AGENTS의 Daily Tech 규칙, `References/Tech Articles/README.md`, `기술 글 템플릿.md`, 최근 문서 한 편, 원본 검증기/추가 전용 preflight/관련 테스트와 CI를 읽었다.

확인한 blob: README `03b0869b5a304a47111b11c91fb518f7dc3096f9`, 템플릿 `61ee964d7f598eb83a7615ea641ab97241113c91`, validator `ae3dc47c6cd196eae57ec52a6f64dfa33befcc82`, preflight `4dc05987a434b21200c485d4b6fa3b668928aca3`.

원본 규칙은 추가 전용·기존 11개 기술 분류·분류별 태그·수집일 기준 파일명/연도·daily-tech의 정확한 staging SHA 검증을 요구한다. 스킬은 원본을 참조하며 자체 schema·템플릿·수집 스크립트를 만들지 않는다. Notion 연결·조회·저장도 사용하지 않았다.

복제 시 `$curationRoot`는 저장소 밖의 새 임시 디렉터리다.

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/guseoh/cs.git "$curationRoot/cs"
git -C "$curationRoot/cs" sparse-checkout set 'References/Tech Articles' .github scripts
git -C "$curationRoot/cs" rev-parse HEAD
```

원격 daily-tech HEAD는 `abdba08446f3aac554489fa91c189e654c58aa97`였다. 그 snapshot과 main 사이에 기사 파일 차이가 있어 자동 초기화·덮어쓰기를 시도하지 않았다. shallow 이력의 ancestry와 진행 중 작업 상태는 확정하지 않았다. staging 원문 전체에 대한 추가 중복 조회는 lazy fetch 비용으로 중단했으므로 **staging을 포함한 게시 직전 유일성은 미검증**이다. 로컬 main snapshot 전체의 URL 검증과 실제 원격 게시 검증은 구분한다.

## 실제 탐색·분석·생성

현재 Codex가 스킬 지침을 직접 적용했다. 별도 모델/서브에이전트 평가나 자동 스킬 선택 검증은 아니다. 검색 결과가 아니라 원문을 열어 제목·발행일·발행처·본문을 확인했다. 개념 학습에 적합한 공급자 원자료와 측정 조건이 명시된 기업 실험 사례를 각각 선정했다. 검색에서 찾은 기존 등록 글은 신규 후보에서 제외했다.

검증 산출물은 다음 두 파일이며 **테스트 fixture일 뿐 실제 아카이브에 등록한 글이 아니다**. 원본 전문/이미지/대형 코드 복제를 피하고 허용 범위의 독립적인 설명으로 핵심 흐름을 작성했다.

- [멱등키·재시도 문서](fixtures/tech-article-curation/2026-11-07-멱등키와-재시도.md): 토스페이먼츠의 [원문](https://docs.tosspayments.com/blog/what-is-idempotency)을 분석. 원문 설명 중 HTTP의 일반 의미는 [RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)와 대조하고 보완 출처를 구분했다. HTTP 코드는 직접 구성한 학습 예제이며 제공사의 실제 endpoint가 아니다.
- [선택적 내재화 문서](fixtures/tech-article-curation/2026-11-07-SNAP-선택적-내재화.md): 토스의 [원문](https://toss.tech/article/54329)을 분석. 원문이 설명한 처리 분기를 가로형 자체 Mermaid로 구성했다. 프로젝트 적용은 제안으로만 적고 projects는 비웠다.

| 대조 항목 | 확인 결과 |
| --- | --- |
| 제목·날짜·출처 | 각 원문 본문에서 확인. collected는 테스트 수집일이며 published와 분리. |
| 개념 정확성 | 응답 재사용이라는 서비스 계약을 HTTP의 일반 멱등성 보장으로 확대하지 않았다. |
| 측정 정확성 | SNAP의 원문 평가/운영 절을 각각 대조했다. 기존 LLM과의 일치와 정답률, 채택 비율, 가상 예시와 실측을 구분했다. 표에 넣지 않은 서빙 측정이나 수치도 요약 결과로 창작하지 않았다. |
| 템플릿 | 정확한 H1, 한 줄 정리, 핵심 내용·왜 읽을까, 하단 원문 링크 유지. 불필요한 한눈에 보기/동일 소제목·자리표시자는 없음. |
| 메타데이터 | type/title/aliases/summary/source/published/collected/url/topic/categories/projects/status/tags를 기존 계약대로 생성. 새 분류 없이 동시성·분산과 AI·개발도구 및 대응 태그 사용. 신규 상태 inbox, 적용 프로젝트 추정 없음. |
| 파일명·범위 | 수집일과 일치하는 YYYY-MM-DD-주제.md. 복제본의 Articles/2026에 새 파일로만 배치. |

## 검사 명령과 결과

`$validationRoot`는 기존 임시 Python 가상환경이며 `PyYAML 6.0.3`과 공식 `skills-ref 0.1.0`(원본 SHA `83021e2be457a9b6679148719c1f6074f0ad975e`)을 사용했다. 저장소 런타임 의존성은 추가하지 않았다.

```powershell
& "$validationRoot/venv/Scripts/python.exe" -X utf8 -m skills_ref.cli validate ./tech-article-curation
& "$validationRoot/venv/Scripts/python.exe" -X utf8 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" ./tech-article-curation
& "$validationRoot/venv/Scripts/python.exe" -X utf8 "$curationRoot/cs/scripts/validate_daily_tech.py"
# 아래 테스트의 작업 디렉터리는 임시 cs 복제본 루트
& "$validationRoot/venv/Scripts/python.exe" -X utf8 -m unittest scripts.test_daily_tech scripts.test_daily_tech_preflight
```

- 형식: **`Valid skill: tech-article-curation`**, **`Skill is valid!`**, exit 0.
- 원본 기준선: **330 articles, URLs unique, metadata and Bases valid**.
- 위 fixture 두 편을 임시 Articles/2026에 복사 후: **332 articles, URLs unique, metadata and Bases valid**, exit 0. 본문 분량을 다듬은 최종 fixture로도 확인했다.
- 기존 테스트: **24 tests, OK (skipped=1)**. symlink 생성이 허용되지 않아 해당 한 건을 skip했다. 최초 테스트 호출은 agent-skills 루트에서 실행해 `No module named scripts`로 실패했으며, 정확한 cs 복제본 루트로 한 번 수정해 통과했다.
- 저장 프로토콜의 실제 원격 CI·마지막 staging SHA·main 반영은 실행하지 않았다. 기존 preflight 테스트의 임시 Git 저장소 검증을 실운영 저장 성공으로 해석하지 않는다.

## Markdown·코드·시각 자료

임시 npm 경로에만 `mermaid 12.3.0`과 `jsdom 26.1.0`을 설치했다. Mermaid의 의존 패키지 `marked`로 두 문서 본문을 파싱해 각각 H1/주요 H2 3개, 표 1개를 확인했다. HTTP fence 1개와 Mermaid fence 1개도 정상 구분됐다. HTTP 예제는 헤더/빈 본문 형식을 직접 대조했으며 네트워크 요청은 보내지 않았다.

```powershell
npm install --prefix "$curationRoot/mermaid-check" --no-save --no-package-lock --ignore-scripts mermaid@12.3.0 jsdom@26.1.0
node "$curationRoot/check-mermaid.mjs" <멱등키-fixture-절대경로> <SNAP-fixture-절대경로>
```

임시 검사 코드는 jsdom의 window/document를 설정한 뒤 `mermaid.initialize({startOnLoad:false})`와 `await mermaid.parse(code)`를 호출했다. 결과는 **`Mermaid parsed: flowchart-v2`**였다. 최초 Node 단독 파싱은 DOMPurify DOM 환경 부재로 실패했고, jsdom을 제공해 한 번 재실행하여 통과했다. 도식 내용을 바꾸거나 검사기를 우회하지 않았다. Obsidian 내장 Mermaid 버전과 GUI 렌더링/레이아웃은 미검증이다.

원문 그림 후보는 확인했으나 이미지 외부 표시의 이용 조건을 확정하지 못했고, 연결된 권리 안내도 404였다. 출처 링크만으로 허가를 추정하지 않아 이미지 임베드·파일 복사를 하지 않았다. 따라서 실제 원문 이미지 렌더링과 지속성은 **미검증/미사용**이며 성공으로 집계하지 않는다. 대체 도식은 자체 재구성임을 표시했다.

## 중복·실패·보존 검사

임시 드라이버에서 원본 `canonical_url`, `validate_note`, `validate_archive`를 재사용했다. 기존 아카이브 파일은 변경 전 bytes를 보관해 비교했다. 드라이버는 저장소 밖에만 두었으며 스킬에는 추가하지 않았다.

| 입력/상황 | 실제 결과 |
| --- | --- |
| 토스 /34481 URL의 host 대문자·후행 slash·utm_source·fragment 변형 | 기존 URL과 동일하게 정규화하여 기존 경로를 찾음. 신규 문서 생성 0건. |
| 신규 fixture와 같은 URL을 대문자 host/후행 slash로 복제한 음성 fixture | 원본 검증기가 duplicate canonical URL을 검출. 음성 fixture만 제거 후 정상 상태 확인. |
| 새 문서의 분류 대응 태그를 임시 제거 | missing nested topic tag 검출. 원래 문서로 복구. |
| `https://toss.tech/article/tech-article-curation-missing-reference` 열기 | 도구에서 접근 불가. 본문을 쓰거나 저장하지 않았고, 도구 오류를 특정 HTTP 상태로 단정하지 않았다. |
| 기존 330개 문서의 status·수집 메타데이터·본문 | bytes 비교 전부 일치. 최종 git diff에 기존 추적 파일 변경 없음. |
| 스케줄러 동시성 | 원격 daily-tech에 파일 차이가 있음을 관찰하고 게시/초기화/merge/force push·설정 변경을 수행하지 않음. 동시 실행 lock이나 실제 scheduler 상태를 검증한 결과는 아님. |

## 최종 범위와 한계

공식 형식, 실제 원문 탐색·직접 분석·학습 문서 생성, 고정 SHA의 전체 아카이브 메타데이터/URL 검증, 기존 파일 보존, Markdown 구조와 가로형 Mermaid 구문을 확인했다. 스킬은 SKILL.md 하나이며 다른 스킬이나 Notion에 의존하지 않는다.

실제 Obsidian GUI, 이미지 표시, HTTP 예제 실행, 클라이언트 자동 호출·독립 모델 평가, scheduler 실제 실행 상태, 진행 중 staging 전체 URL, 원격 쓰기 권한·CI/게시 결과는 미검증이다. 이번 작업은 스킬 구현과 테스트 산출물만 dev에 반영하며 실제 아카이브/스케줄러를 변경하거나 main에 병합하지 않는다.

## 스케줄러 비교 후속 보완 (2026-11-07)

- 운영 스케줄러의 최신 저장 지침과 대조해 원격 GitHub 연결의 개별 URL 전수 조회 금지, 스테이징 이후 CI 전체 중복 검사, `daily-tech` 단순 behind 상태 처리 문구를 보완했다.
- SNAP과 멱등성 fixture의 문제 배경·처리 경계·검증 결과·학습 적용 조건을 실제 공개 원문에 근거해 확장했다. SNAP의 6일간 입력 토큰 약 76억/출력 토큰 약 4,520만 감소 및 L4 GPU 서빙 테스트 1,203 requests/s, p50 9.02ms, p99 15.23ms는 [원문](https://toss.tech/article/54329)의 별도 운영/부하 시험 수치다. 멱등키/저장·재시도 흐름은 [토스페이먼츠 원문](https://docs.tosspayments.com/blog/what-is-idempotency)과 대조했다.
- 기존 보고서의 **332 articles / 24 tests(1 skipped) / Mermaid 파싱 통과는 이 후속 편집 이전의 기록**이다. 이번 편집 후 원본 아카이브 전체 검증·단위 테스트·Mermaid 파싱·Obsidian 렌더링·실제 스케줄러 게시를 재실행했다고 주장하지 않는다. Codex 로컬 dev에서 이 변경을 가져온 뒤 관련 검증을 다시 실행해야 한다.
- 변경 범위는 스킬 1개, 테스트 fixture 2개, 검증 보고서 1개이며 원본 `guseoh/cs`, GitHub `main`과 스케줄러 설정은 이 Git 작업에서 변경하지 않았다.
