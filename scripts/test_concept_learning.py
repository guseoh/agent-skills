"""Deterministic concept-learning structure, packaging and safety-contract tests.

This suite never invokes an LLM and cannot certify teaching quality or client installation.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "concept-learning"
EXTRAS = (
    "references/teaching-rules.md",
    "references/subject-guidance.md",
    "references/quality-cases.md",
    "references/project-instructions.md",
    "references/topic-context.md",
    "references/source-and-visual-guidance.md",
    "references/response-quality-gate.md",
    "references/research-first-workflow.md",
    "references/response-modes.md",
)


class ConceptLearningContract(unittest.TestCase):
    def source(self, relative: str) -> str:
        return (ROOT / NAME / relative).read_text(encoding="utf-8")

    def test_valid_skill_identity(self) -> None:
        skill = self.source("SKILL.md")
        self.assertTrue(skill.startswith("---\nname: concept-learning\ndescription: "))
        self.assertRegex(skill, r"(?s)^---\nname: concept-learning\n.*?\n---\n")
        self.assertIn("# Concept learning", skill)

    def test_bundle_includes_identical_references(self) -> None:
        for relative in ("SKILL.md", *EXTRAS):
            with self.subTest(relative=relative):
                canonical = ROOT / NAME / relative
                packaged = ROOT / "plugins" / NAME / "skills" / NAME / relative
                self.assertTrue(canonical.is_file())
                self.assertTrue(packaged.is_file())
                self.assertEqual(canonical.read_bytes(), packaged.read_bytes())

    def test_user_selected_topic_is_primary(self) -> None:
        skill = self.source("SKILL.md")
        context = self.source("references/topic-context.md")
        cases = self.source("references/quality-cases.md")
        instructions = self.source("references/project-instructions.md")
        for required in ("신입~2년 차", "다형성1부터 진행하자", "Bean 생명주기", "진행하자", "설명해줘"):
            with self.subTest(required=required):
                self.assertIn(required, skill)
        self.assertIn("로드맵을 설계·편집·병합", context)
        self.assertIn("같은 교수법", cases)
        self.assertIn("진도를 관리하지 않는다", instructions)
        self.assertNotIn("로드맵 진행 규칙", skill)
        self.assertNotIn("로드맵을 따라 한 주제씩", instructions)
        self.assertFalse((ROOT / NAME / "references/roadmap-workflow.md").exists())

    def test_korean_sources_images_and_paragraphs(self) -> None:
        skill = self.source("SKILL.md")
        teaching = self.source("references/teaching-rules.md")
        sources = self.source("references/source-and-visual-guidance.md")
        cases = self.source("references/quality-cases.md")
        for term in ("인과관계", "글머리표", "문단", "소제목"):
            with self.subTest(style=term):
                self.assertTrue(term in skill or term in teaching or term in cases)
        for term in ("한국어 개인 개발 기술 블로그", "이미지", "원본",
                     "출처", "이용 조건", "무단 복제", "원문을 열지 않아도"):
            with self.subTest(source_rule=term):
                self.assertIn(term, sources)
        self.assertIn("한 줄 문장/한 줄 문단", cases)
        self.assertIn("코드 블록 뒤", skill)

    def test_independent_korean_blogs_and_exclusions(self) -> None:
        skill = self.source("SKILL.md")
        sources = self.source("references/source-and-visual-guidance.md")
        rules = self.source("references/teaching-rules.md")
        for term in ("Tistory", "Velog", "Medium", "GitHub.io", "hudi.blog",
                     "한국 IT 기업", "한빛미디어", "위키독스"):
            with self.subTest(term=term):
                self.assertIn(term, sources)
        self.assertIn("개인 개발 기술 블로그", skill)
        self.assertIn("한빛미디어", rules)
        self.assertIn("위키독스", rules)
        self.assertIn("참고 링크 후보에서 제외", sources)

    def test_image_priority_deeper_learning_and_format_balance(self) -> None:
        skill = self.source("SKILL.md")
        sources = self.source("references/source-and-visual-guidance.md")
        cases = self.source("references/quality-cases.md")
        for term in ("실제 이미지", "도식", "보조", "출처", "이용 조건", "본문"):
            with self.subTest(term=term):
                self.assertIn(term, sources)
        for term in ("심화", "키워드", "글머리표", "Markdown 표", "무조건"):
            with self.subTest(term=term):
                self.assertTrue(term in skill or term in sources)
        self.assertIn("객체지향 강의에 대한 실제 실패 교정", cases)
        self.assertIn("이미지 실패", cases)
        self.assertIn("한빛미디어·위키독스", cases)

    def test_quality_gate_enforces_preaudit_and_revision(self) -> None:
        skill = self.source("SKILL.md")
        gate = self.source("references/response-quality-gate.md")
        sources = self.source("references/source-and-visual-guidance.md")
        rules = self.source("references/teaching-rules.md")
        self.assertIn("답변 초안 작성 후, 최종 출력 전에", skill)
        self.assertIn("신입~2년 차", skill)
        self.assertIn("신입~2년 차", rules)
        for label in ("G1.", "G2.", "G3.", "G4.", "G5.", "G6.", "G7.", "G8."):
            with self.subTest(label=label):
                self.assertIn(label, gate)
        for term in ("PASS", "REVISE", "LIMITATION", "다시 검사", "소제목", "실제 이미지", "파비콘", "중복", "저작권", "실제 모델 응답"):
            with self.subTest(term=term):
                self.assertIn(term, gate)
        for term in ("테코블", "주요 소제목", "핵심 하위 주제"):
            with self.subTest(term=term):
                self.assertIn(term, sources)
        self.assertIn("CI는 정적", gate)
        self.assertIn("체크리스트 자체를 학습자에게 자동 출력하지 않는다", skill)

    def test_research_first_precedes_drafting(self) -> None:
        skill = self.source("SKILL.md")
        research = self.source("references/research-first-workflow.md")
        gate = self.source("references/response-quality-gate.md")
        self.assertIn("## 주제별 강의 작성 절차 — 자료 조사 우선", skill)
        self.assertLess(skill.index("1. **요청 모드를 정한 뒤 주제를 분석한다."), skill.index("5. **소제목별 검증된 근거로 모드에 맞게 작성한다."))
        self.assertIn("자료 조사와 소제목별 근거 매핑을 마치기 전", skill)
        self.assertIn("G0. 조사 우선 충족", gate)
        self.assertIn("단계 A/B/C", gate)
        self.assertIn("단계 B/C로 되돌아가", research)
        for label in ("단계 A", "단계 B", "단계 C", "단계 D", "근거 지도", "소제목"):
            with self.subTest(label=label):
                self.assertIn(label, research)

    def test_book_keyword_discovery_and_image_evidence_states(self) -> None:
        research = self.source("references/research-first-workflow.md")
        sources = self.source("references/source-and-visual-guidance.md")
        cases = self.source("references/quality-cases.md")
        skill = self.source("SKILL.md")
        for term in ("《오브젝트》", "《객체지향의 사실과 오해》", "공개 목차", "읽지 않은", "다형성", "컴파일타임"):
            with self.subTest(term=term):
                self.assertIn(term, research)
        for term in ("FOUND_AND_DISPLAYABLE", "FOUND_LINK_ONLY", "NOT_FOUND", "NOT_APPLICABLE", "TOOL_UNAVAILABLE"):
            with self.subTest(state=term):
                self.assertIn(term, research)
                self.assertIn(term, sources)
        for term in ("파비콘", "s2/favicons", "실제", "CI"):
            with self.subTest(term=term):
                self.assertIn(term, cases)
        self.assertIn("강의 초안을 쓰기 전에", skill)
        self.assertNotIn("mcpServers", skill)
        self.assertNotIn("hooks", skill)

    def test_explain_vs_summarize_modes(self) -> None:
        skill = self.source("SKILL.md")
        modes = self.source("references/response-modes.md")
        research = self.source("references/research-first-workflow.md")
        gate = self.source("references/response-quality-gate.md")
        cases = self.source("references/quality-cases.md")
        for token in ("설명해줘", "정리해줘", "요약해줘", "EXPLAIN", "SUMMARIZE"):
            with self.subTest(token=token):
                self.assertIn(token, modes)
                self.assertIn(token, skill + research)
        self.assertIn("첨부 파일", modes)
        self.assertIn("실제 확인 가능한", modes)
        self.assertIn("SUMMARIZE", gate)
        self.assertIn("EXPLAIN", gate)
        self.assertIn("정리해줘", cases)
        self.assertIn("설명과 정리", self.source("references/project-instructions.md"))

    def test_book_relevance_before_book_keyword_discovery(self) -> None:
        skill = self.source("SKILL.md")
        research = self.source("references/research-first-workflow.md")
        sources = self.source("references/source-and-visual-guidance.md")
        cases = self.source("references/quality-cases.md")
        self.assertIn("관련 없는 주제에는 자동으로 가져오지 않는다", skill)
        self.assertIn("Spring Bean 생명주기에서는 기본 탐색 대상이 아니다", research)
        self.assertIn("관련 없는 책은 검색에 포함하지 않고", sources)
        self.assertIn("무관한 객체지향 서적을 무조건 인용", cases)
        self.assertIn("주제 일치 여부", research)
        self.assertIn("읽지 않은 책", skill)
        self.assertNotIn("hooks", skill)
        self.assertNotIn("mcpServers", skill)

    def test_explain_source_claim_and_image_display_gates(self) -> None:
        skill = self.source("SKILL.md")
        gate = self.source("references/response-quality-gate.md")
        research = self.source("references/research-first-workflow.md")
        sources = self.source("references/source-and-visual-guidance.md")
        cases = self.source("references/quality-cases.md")
        for term in ("주장-출처", "소제목", "직접", "정적 메서드"):
            with self.subTest(source=term):
                self.assertIn(term, research + gate)
        for term in ("파비콘", "미디어", "링크", "렌더링", "실제 개념 이미지"):
            with self.subTest(visual=term):
                self.assertIn(term, sources + gate)
        self.assertIn("google.com/s2/favicons", cases)
        self.assertIn("Markdown 텍스트 링크", cases)
        self.assertIn("이미지 자체", skill)
        self.assertIn("표시 성공", gate)

    def test_explain_book_in_body_and_semantically_complete_code(self) -> None:
        skill = self.source("SKILL.md")
        gate = self.source("references/response-quality-gate.md")
        cases = self.source("references/quality-cases.md")
        sources = self.source("references/source-and-visual-guidance.md")
        self.assertIn("책 이름과 장 번호만 맨 끝에", skill)
        self.assertIn("본문 단원", gate)
        self.assertIn("《오브젝트》", cases)
        self.assertIn("discountPolicy.discount(price)", cases)
        self.assertIn("Spring DI는 반드시 인터페이스가 있어야 가능한 기술이 아니다", cases)
        self.assertIn("동일한", gate)
        self.assertIn("컴파일타임 의존성과 런타임 의존성", sources)
        self.assertIn("SUMMARIZE는 유지", cases)
        self.assertIn("CI는 정적", gate)

    def test_complete_teaching_rules(self) -> None:
        guidance = self.source(EXTRAS[0])
        numbers = [int(n) for n in re.findall(r"(?m)^(\d{1,2})\. ", guidance)]
        self.assertEqual(numbers, list(range(1, 27)))
        for term in ("~이다", "공식 문서", "후속", "실습", "비밀", "로드맵"):
            self.assertIn(term, guidance)

    def test_subject_coverage_and_quality_cases(self) -> None:
        subjects = self.source(EXTRAS[1])
        cases = self.source(EXTRAS[2])
        for term in ("Java", "Spring Framework", "JPA", "Security", "DB", "Linux", "시스템 설계", "AI"):
            with self.subTest(subject=term):
                self.assertIn(term, subjects)
        for term in ("다형성", "트랜잭션", "flush", "inactive", "후속", "보안"):
            with self.subTest(case=term):
                self.assertIn(term, cases)

    def test_untrusted_material_and_write_boundaries(self) -> None:
        skill = self.source("SKILL.md")
        for term in ("비신뢰 자료", "프롬프트", "비밀키", "자동 명령 실행",
                     "진도", "자동으로", "외부 게시", "명시적", "CSForge"):
            with self.subTest(boundary=term):
                self.assertIn(term, skill)
        self.assertNotIn("mcpServers", skill)

    def test_plugin_manifest_and_private_catalog(self) -> None:
        manifest = json.loads((ROOT / "plugins" / NAME / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], NAME)
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)
        catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entries = [item for item in catalog["plugins"] if item["name"] == NAME]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/concept-learning"})

    def test_project_instructions_do_not_promise_memory(self) -> None:
        instructions = self.source(EXTRAS[3])
        for term in ("새 채팅", "자동", "학습 진도", "로드맵"):
            self.assertIn(term, instructions)

    def test_no_credential_shape_in_new_files(self) -> None:
        paths = [ROOT / NAME / p for p in ("SKILL.md", *EXTRAS)]
        paths.append(ROOT / "tests/concept-learning.md")
        for path in paths:
            content = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertNotRegex(content, r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}")
                self.assertNotRegex(content, r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----")


if __name__ == "__main__":
    unittest.main()
