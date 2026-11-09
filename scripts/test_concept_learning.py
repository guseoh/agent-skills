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
    "references/roadmap-workflow.md",
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

    def test_roadmap_first_learning_contract(self) -> None:
        skill = self.source("SKILL.md")
        workflow = self.source("references/roadmap-workflow.md")
        examples = self.source("references/quality-cases.md")
        prompts = self.source("references/project-instructions.md")
        for required in ("로드맵 기반 강의 진행", "로드맵 진행 규칙", "현재 로드맵 주제 강의"):
            self.assertIn(required, skill)
        for required in ("Spring", "Database", "이어서", "다음 주제", "단독 질문", "완료 여부", "개요를 열거"):
            self.assertIn(required, workflow)
        for required in ("Spring 학습 시작하자", "Database 학습 이어서 진행해"):
            self.assertIn(required, examples)
        self.assertIn("과목별 로드맵을 따라 한 주제씩", prompts)

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
