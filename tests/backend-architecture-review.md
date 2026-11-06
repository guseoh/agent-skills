# backend-architecture-review 검증

검증일: 2026-11-07. 구현 기준: `dev`의 `0758b37`. 기존 wiki-capture 파일은 변경하지 않았다.

## 방법과 범위

공식 형식 검증과 현재 Codex가 스킬 지침을 직접 적용한 설계 리뷰를 수행했다. 실제 공개 Java/Spring 프로젝트의 고정 커밋을 읽고, 같은 도메인의 신규 설계 연습 및 자료 부족 사례와 함께 평가했다. 아래는 실제로 작성한 리뷰 결과다. 별도 모델/서브에이전트의 독립 평가나 CLI 도구 통합 검증으로 주장하지 않는다. 분석 대상 코드·설계·설정은 수정하지 않았고 서버·DB·테스트·부하 실험도 실행하지 않았다.

## 공식 형식 검증

[Agent Skills 명세](https://agentskills.io/specification)의 공식 reference 구현 `skills-ref 0.1.0`(원본 SHA `83021e2be457a9b6679148719c1f6074f0ad975e`)과 번들 검증기를 사용했다. `$validationRoot`는 이전 검증 때 생성한 저장소 밖의 임시 가상환경 경로다. `PyYAML 6.0.3`이 그 환경에만 설치되어 있다.

```powershell
& "$validationRoot/venv/Scripts/python.exe" -X utf8 -m skills_ref.cli validate ./backend-architecture-review
& "$validationRoot/venv/Scripts/python.exe" -X utf8 C:/Users/guseo/.codex/skills/.system/skill-creator/scripts/quick_validate.py ./backend-architecture-review
```

결과: 각각 **`Valid skill: backend-architecture-review`**, **`Skill is valid!`**, exit 0. 필수 frontmatter, 이름/폴더 일치, description 검증 통과. 스킬은 `SKILL.md` 하나로 구성하며 로컬 참조·스크립트·다른 스킬 의존성이 없다.

## 사례 A — 신규 예약 백엔드 설계

실제 Petclinic의 방문 기록 도메인에서 파생한 **가상 신규 요구사항**이다. Petclinic 자체의 제품 요구나 실측 수치를 뜻하지 않는다.

입력: Java 21/Spring Boot 3.5/Spring Framework 6.2, PostgreSQL 16. 개발·운영 2명, 예상 피크 20 requests/s(가정), 고정된 30분 슬롯. 같은 병원·수의사·시작 시각에는 활성 예약 하나만 허용한다. 취소 후 재예약과 예약 이력 보존, 네트워크 재시도의 중복 예약 방지, 병원 간 접근 격리, 커밋된 예약 알림의 최종 전달이 필요하다.

제안: 단일 애플리케이션과 DB. 예약 여부를 SELECT로 확인한 뒤 INSERT한다. public `book()`은 트랜잭션이 없고 같은 빈의 public `persist()`를 직접 호출하며 `persist()`에만 `@Transactional`이 있다. `persist()`에서 repository 저장 후 SMS를 호출한다. 병원 ID는 요청 값으로 받으며 별도 인가 설계는 없다. 알림 내구성·멱등 키·DB 슬롯 제약은 없다.

### 적용한 리뷰

단일 앱/DB는 현재 팀과 예상 규모의 합리적인 기준선이다. 다만 명시된 불변식을 만족하지 못하는 경로는 출시 전 해결해야 한다. 다음 판단은 제공한 설계와 공식 의미를 근거로 하며 런타임 재현 결과는 아니다.

| 구분 | 발생 과정과 영향 | 최소 대응·대안·비용 |
| --- | --- | --- |
| 심각 — 슬롯 경쟁 | T1과 T2가 같은 슬롯을 모두 빈 상태로 읽고 각각 INSERT하면 두 활성 예약이 생길 수 있다. 트랜잭션 존재만으로 check-then-insert가 직렬화되지는 않는다. | 슬롯 키 필드는 NOT NULL로 두고 활성 예약에만 적용되는 유일 인덱스를 우선 검토한다. 취소 이력을 남기므로 모든 상태에 대한 단순 UNIQUE는 재예약 요구와 충돌한다. 대안은 미리 만든 슬롯 행의 조건부 갱신/잠금이며, 빈 예약 조회에 대한 행 잠금만으로는 없는 행을 보호한다고 가정하지 않는다. 고경합에서는 대기·실패 처리 비용을 비교한다. |
| 심각 — 재시도 의미 부재 | 저장은 성공했으나 응답이 유실되면 클라이언트는 실패로 보고 재시도할 수 있다. 슬롯 제약만으로 원래 성공 결과를 복원하지는 못한다. | 사용자/병원·연산에 맞게 범위를 정한 멱등 키와 결과/요청 fingerprint를 함께 보존한다. 동일 키·동일 요청은 기존 결과, 동일 키·다른 요청은 명시적 충돌로 처리한다. 보관 기간과 처리 중 상태의 복구 비용을 정해야 한다. |
| 심각 — 유스케이스 트랜잭션 오해 | 기본 프록시 방식에서 자기 호출은 `persist()`의 트랜잭션 조언을 통과하지 않는다. repository 저장 자체의 트랜잭션 가능성과 전체 book 유스케이스의 원자성은 다르다. SMS 오류가 DB 저장을 되돌린다고 보장할 수 없다. | 외부에서 프록시를 통과하는 유스케이스 경계를 둔다. 이 변경도 외부 SMS와 DB를 한 원자적 자원으로 만들지는 않는다. 대안인 명시적 transaction template은 경계를 분명히 하지만 트랜잭션 코드 결합 비용이 있다. |
| 심각 — 알림 유실 | DB 커밋 후 프로세스가 종료되면 단순 후처리 알림은 유실될 수 있다. 커밋 전 전송이면 DB 실패에도 알림만 전달될 수 있다. | 최종 전달이 필수이므로 예약과 전달할 이벤트를 DB에 함께 저장하고 작은 재시도 worker를 두는 방안을 검토한다. 중복 전달을 허용하는 모델과 수신 측 멱등성, 운영 대기열·재시도 한계가 필요하다. 단순 after-commit callback은 이 요구의 내구성을 보장하지 않는다. Kafka는 필수 전제가 아니다. |
| 심각 — 병원 간 인가 공백 | 요청 clinicId를 신뢰하면 인증된 다른 병원의 ID를 넣어 접근할 수 있다는 설계상 공백이 있다. 이는 인증 자체의 성공과 별개다. | 인증 주체의 권한으로 병원 범위를 제한하고 조회/갱신에도 동일하게 적용한다. gateway 등 다른 통제가 있다는 증거는 제공되지 않았다. 실제 취약점 재현 완료라고 주장하지 않는다. |
| 선택적 개선 | 기능이 늘 때 예약·고객·알림의 변경 이유가 다르다. | 같은 배포 안에서 모듈/인터페이스 경계를 먼저 분리한다. 별도 서비스/DB는 원격 실패·정합성·배포 비용을 추가하므로 독립 팀·배포 요구가 생길 때 재검토한다. |

추천: 단일 앱/DB를 유지하고 명시된 정합성·인가·알림 내구성부터 보완한다. Redis/Kafka/Kubernetes를 피크 가정만으로 추가하지 않는다. 변동 길이 예약으로 바뀌면 같은 시작 시각 유일성만으로 시간 구간 겹침을 막을 수 없으므로 다시 모델링한다. worker 지연, 슬롯별 경합/실패, DB 대기와 실제 응답 지연을 관측해 후속 선택을 판단한다. 숫자 기반 도입 임계치는 만들지 않았다.

제안한 검증(미실행): 같은 슬롯에 두 요청을 동시에 진입시켜 활성 예약 한 건 확인; 응답 유실 뒤 같은 멱등 키 재전송 시 같은 결과 확인; 취소 이력 유지 후 재예약; 커밋 직후 프로세스 종료 후 알림 복구·중복 처리 확인; 다른 병원 ID에 대한 읽기/쓰기 거부 확인. 통과 여부는 보고하지 않는다.

근거: [Spring Framework 6.2의 프록시 트랜잭션과 자기 호출](https://docs.spring.io/spring-framework/reference/6.2/data-access/transaction/declarative/annotations.html), [PostgreSQL 16 제약과 부분 유일 인덱스](https://www.postgresql.org/docs/16/ddl-constraints.html). 공식 근거로 충분한 쟁점이어서 한국 블로그의 운영 사례를 추가로 조사하지 않았다.

## 사례 B — 실제 Java/Spring 프로젝트

대상: [Spring Petclinic](https://github.com/spring-projects/spring-petclinic/tree/500158f732419217507c7656904b8e6aa1bcc0d6)의 방문 등록 경로. 공개 학습용 샘플이며 실제 운영 시스템이나 사례 A의 예약 요구사항과 동일하지 않다. 임시 shallow/sparse 복제본을 읽었다.

```powershell
git clone --depth 1 --filter=blob:none --sparse https://github.com/spring-projects/spring-petclinic.git "$backendReviewRoot/petclinic"
git -C "$backendReviewRoot/petclinic" sparse-checkout set src/main/java/org/springframework/samples/petclinic/owner src/main/resources/db/h2 src/test/java/org/springframework/samples/petclinic/owner
git -C "$backendReviewRoot/petclinic" rev-parse HEAD
```

확인한 SHA: `500158f732419217507c7656904b8e6aa1bcc0d6`. pom의 선언은 Boot 4.1.0 / Java 17이며 실제 실행 JDK와 유효 의존성 트리는 확인하지 않았다. 오래된 소개 슬라이드가 현재 구현과 다를 수 있다는 readme 경고도 확인했다.

| 실제 근거 | 리뷰 결과 |
| --- | --- |
| [VisitController.java](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/VisitController.java#L64): owner 조회, 해당 owner 안에서 pet 검색, 검증 후 save. [OwnerRepository](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java#L36)는 JpaRepository 상속. | 단순한 방문 기록 기능에는 직접 repository 사용이 이해 가능하다. Service 계층 부재만으로 심각한 결함이나 모든 저장의 무트랜잭션을 주장하지 않는다. 여러 저장소/외부 효과가 생길 때 유스케이스 경계를 명시하는 선택을 재검토한다. 상속 CRUD의 트랜잭션 기본 의미는 [Spring Data 문서](https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html)와 대조했으며 해당 배포의 유효 버전/설정까지 실행 검증한 것은 아니다. |
| [Owner.getPet](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/Owner.java#L129)은 조회된 소유자의 pet에서 찾는다. | owner와 pet의 관계 확인과 로그인 주체의 리소스 인가는 다르다. 외부 공개·다중 병원 서비스로 전환한다면 객체 단위 인가를 반드시 확인할 조건부 위험이다. gateway/전역 보안 설정과 실제 배포는 조사하지 않았으므로 현재 운영 인가 취약점으로 단정하지 않는다. |
| [Owner의 pets](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/Owner.java#L67)와 [Pet의 visits](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/Pet.java#L56)는 EAGER. application.properties에 open-in-view=false, batch fetch size=16. | 단순 화면에서 객체 그래프 접근이 쉬운 대가로 방문 이력이 큰 소유자의 조회 범위가 커질 수 있다. **측정 전 성능 위험 후보**다. EAGER만 보고 특정 N+1/SQL 횟수나 지연을 단정하지 않는다. 대표 데이터의 SQL·메모리를 먼저 측정하고 필요할 때 조회 전용 projection/페이징을 비교한다. LAZY 일괄 전환은 트랜잭션 밖 접근 경로도 검토해야 한다. |
| [VisitControllerTests](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/test/java/org/springframework/samples/petclinic/owner/VisitControllerTests.java#L44)는 WebMvcTest와 모의 repository 사용. | HTTP 검증·뷰 경로 테스트의 존재는 확인했다. DB cascade·트랜잭션·동시성·운영을 보장하는 실행 결과로 해석하지 않는다. 테스트는 읽기만 했으며 통과 여부는 확인하지 않았다. |
| [H2 visits 스키마](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/resources/db/h2/schema.sql#L58)는 pet/date/description과 FK·인덱스를 포함한다. | 사례 A의 수의사·슬롯·활성 예약 요구를 원본에 소급해 “중복 예약 결함”으로 지적하지 않는다. H2 스키마를 MySQL/PostgreSQL 배포의 확인 사실로 확대하지 않는다. |

판정: 이 범위에서 확인된 심각한 설계 결함은 선언하지 않았다. 사용 목적과 변화 조건을 붙인 경계/조회 개선 후보를 제시했다. 이름만 바꾼 계층 추가, MSA·클라우드 이전을 권고하지 않았다. 전체 보안·DB 배포·운영 안전성을 인증한 결과는 아니다.

## 사례 C — 근거 부족과 과도한 설계 권고 방지

입력: “Controller→Service→Repository 그림만 있다. 사용자 수·피크·쿼리·응답시간·팀 규모는 모른다. 느릴 것 같으니 Kafka, Redis와 MSA를 도입해야 하나?”

실제 리뷰: 그림은 책임 계층의 의도만 보여 주며 병목·실제 의존 방향·트랜잭션 범위를 증명하지 않는다. 기술 도입 결론은 **보류**한다. 우선 문제가 되는 요청 하나, 목표 지연, 실제 지연 분포/쿼리·외부 대기, 데이터량과 배포/운영 제약을 요청한다. 자료 없이도 “조회 캐시는 무효화와 stale 허용 범위가 필요하고, 비동기 큐는 동기 응답의 정합성 계약을 바꿀 수 있다”는 조건부 비교는 가능하다. 임의 성능 수치·클라우드 구성·확인하지 않은 출처는 만들지 않는다.

선택지는 현재 구조 유지/핫패스 조회 개선/캐시/비동기화/분리의 순서로 **상황에 따라** 검토하며 이 순서를 의무적 마이그레이션 단계로 만들지 않았다. 근거 없는 심각 결함과 기술 도입 권고는 없었다.

## 품질 판정과 한계

| 검증 기준 | 관찰한 결과 |
| --- | --- |
| 신규/기존 구분 | 신규의 확정 조건과 가정, 실제 샘플의 코드·문서·미확인 운영 사실을 구분했다. |
| 대안의 구체성 | 유일 제약과 슬롯 행 갱신/잠금, 로컬 경계와 외부 효과, callback과 내구성 있는 전달을 실패 순서·비용·적용 조건으로 비교했다. |
| 과도한 설계 방지 | 규모가 작은 신규 사례에서 필요한 불변식을 지키면서 단일 앱/DB를 유지했고, 원본 샘플에 불필요한 서비스 계층·MSA를 강요하지 않았다. |
| 심각/선택적 구분 | 신규의 명시적 요구 위반, 기존의 조건부 위험/개선 후보, 자료 부족의 보류를 구분했다. |
| 독립·읽기 전용 | 다른 스킬 연계, 자동 기록/수정/배포, 분석 대상의 테스트 자동 실행 없이 리뷰했다. |

확인한 것은 공식 형식과 위 입력에 대한 현재 Codex의 분석 결과다. 독립 모델의 반복 실행·자동 선택·ChatGPT/Codex 클라이언트 통합, 실제 경쟁 요청/장애/성능·인가 재현, 한국 기술 블로그 검색 동작은 **미검증**이다. 신규 사례는 가상 설계이며 실제 운영 장애의 재현 보고가 아니다. 공개 샘플 복제본의 `git status --short`는 변경 없이 끝났다. 영구 추가 파일은 스킬과 이 검증 기록뿐이다.
