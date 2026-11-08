# CS 학습 시각화 — 세 가지 기준 사례와 검증

기준일: 2026-11-08. 이 기록은 **스킬 규칙과 직접 제작한 SVG fixture의 검증 계약**이다. 실제 CSForge Reader 통합 및 브라우저 시각 검증 완료 보고가 아니다.

## 근거와 재사용 경계

- [Hello Algo](https://github.com/krahets/hello-algo)에서는 개념 설명에 맞춘 그림의 순서·배치 방식을 참고했다. 원본 그림을 복제하지 않았으며 해당 프로젝트의 콘텐츠 라이선스는 CC BY-NC-SA 4.0이다.
- [Learn DSA Visually](https://github.com/rajeshgoyalg/Learn-Data-Structures-and-Algorithms-Visually)에서는 독립 SVG와 CSS만으로 설명용 시각화를 구성하는 방식을 참고했다. 이 프로젝트는 MIT 라이선스를 명시한다.
- 예제 SVG 세 개는 이 플러그인을 위해 새로 제작한 검증 fixture다. 원본 사이트의 이미지 파일을 포함하지 않는다.

## 1. Heap — 완전 이진 트리와 배열

[예제 SVG](../cs-learning-visualization/examples/heap-tree-array.svg): 배열 `[2,4,7,9,8,11,13]`. 트리의 index 0~6과 0-based 배열 위치가 일치해야 한다. 모든 `i>0`에 대해 `a[(i-1)//2] <= a[i]`. 값만 맞고 인덱스가 다른 그림, 또는 힙의 정렬된 배열이라고 암시하는 그림은 불합격이다.

## 2. Java — 참조값 복사와 매개변수 재할당

[예제 SVG](../cs-learning-visualization/examples/java-pass-by-value.svg): 호출 직후 `member→A, param→A`. 메서드 안에서 `param = new Member()` 실행 직후 `member→A, param→B`. 객체의 필드를 변경한 것이 아니고 호출자 변수도 바뀌지 않는다. 메서드 종료 전 상태를 그렸다는 점과 물리적 JVM 메모리 구조를 주장하지 않는다는 점을 유지한다. 근거: [JLS 15.12.4.2](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.12.4.2).

## 3. TCP — 바이트 기반 송신 윈도우 이동

[예제 SVG](../cs-learning-visualization/examples/tcp-sliding-window.svg): 한 세그먼트의 데이터가 100B이고, 초기에 송신 가능한 범위가 1000~1399이다. 1000~1399를 송신한 뒤 누적 `ACK=1200` 수신 시 1000~1199가 확인되며 송신 윈도우는 1200~1599로 움직인다. 1200~1399는 미확인 상태이고 1400~1599는 새로 전송 가능하다. `rwnd=400B`, `cwnd>=400B`, 손실 없음이라는 가정이 있다. 실제 TCP ACK가 세그먼트 일련번호라는 설명은 불합격이다. 근거: [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293).

## 검증 방법

```bash
python scripts/package_plugins.py --check
python scripts/check_learning_visuals.py
python scripts/check_markdown.py
skills-ref validate cs-learning-visualization
skills-ref validate plugins/cs-learning-visualization/skills/cs-learning-visualization
```

정적 검사 범위: 패키지 내용 일치, SVG XML·viewBox·title/desc·대비용 테마 규칙, 금지 태그, 세 예제의 명시된 값/상태를 확인한다. 이러한 검사는 **코드 내부 메타데이터에 대한 검증**이므로 모든 선의 위치·텍스트 렌더링·설명 정확성을 인증하지 않는다.

수동 검증(아직 독립 브라우저로 미실행): [예제 갤러리](../cs-learning-visualization/examples/index.html)를 데스크톱에서 라이트/다크, 900px 및 1280px 콘텐츠 폭으로 열고 모든 레이블·화살표·배경·대비·본문 균형을 확인한다. Java 참조의 화살표가 실제 객체를 가리키는지, Heap 인덱스 0~6이 배열에 대응하는지, TCP ACK와 강조된 윈도우 범위가 그림 설명과 맞는지 사람의 눈으로 점검한다.

CSForge Reader에 적용할 때는 렌더링 보안, 스타일 격리, 기존 콘텐츠의 식별자 및 사용자 이력 보존, 실제 Reader에서의 시각 QA를 추가로 검증한다.

## 판정 상태

- 세 사례와 SVG 제작 규칙: **초안 구현**
- CI 정적 검사: PR에서 확인 예정
- 브라우저 라이트/다크 시각 QA: **미실행**
- CSForge Reader 통합·프로덕션 반영: **범위 밖·미실행**
