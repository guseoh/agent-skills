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
        for required in ("취업 준비생", "다형성1부터 진행하자", "Bean 생명주기", "진행하자", "설명해줘"):
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
