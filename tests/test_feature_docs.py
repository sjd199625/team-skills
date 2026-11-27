import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = (
    Path(__file__).parents[1]
    / ".agents"
    / "skills"
    / "frontend-workflow"
    / "scripts"
    / "feature_docs.py"
)
SPEC = importlib.util.spec_from_file_location("feature_docs", SCRIPT)
feature_docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(feature_docs)


class StateTests(unittest.TestCase):
    def test_state_without_pc(self):
        text = feature_docs.state_yaml(
            "demo",
            {"path": "/tmp/h5", "branch": "main", "commit": "abc"},
            {"path": "", "branch": "", "commit": ""},
        )
        self.assertNotIn("frontend_pc", text)

    def test_state_with_pc(self):
        text = feature_docs.state_yaml(
            "demo",
            {"path": "/tmp/h5", "branch": "main", "commit": "abc"},
            {"path": "", "branch": "", "commit": ""},
            {"path": "/tmp/pc", "branch": "feature/pc", "commit": "def"},
        )
        self.assertIn("frontend_pc", text)
        self.assertIn("feature/pc", text)

    def test_section_value_accepts_comment(self):
        text = "repos:\n  frontend_pc: # optional\n    branch: \"feature/pc\"\n"
        self.assertEqual(feature_docs.state_section_value(text, "frontend_pc", "branch"), "feature/pc")


class GateTests(unittest.TestCase):
    def run_gate(self, phase, gates):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = (
                f"phase: {phase}\n"
                "gates:\n"
                + "".join(f"  {key}: {'true' if value else 'false'}\n" for key, value in gates.items())
            )
            state_path = repo / "docs" / "demo" / "workflow-state.yaml"
            state_path.parent.mkdir(parents=True)
            state_path.write_text(state, encoding="utf-8")
            args = SimpleNamespace(repo=str(repo), feature="demo", phase=phase)
            feature_docs.cmd_gate(args)

    def test_design_gate_passes(self):
        self.run_gate("design", {})

    def test_test_gate_requires_build(self):
        with self.assertRaises(SystemExit):
            self.run_gate("test", {"design_confirmed": True, "build_passed": False})

    def test_test_gate_passes_after_build(self):
        self.run_gate("test", {"design_confirmed": True, "build_passed": True})


class CheckTests(unittest.TestCase):
    def run_check(self, phase, artifacts, state_text):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            feature_dir = repo / "docs" / "demo"
            feature_dir.mkdir(parents=True)
            (feature_dir / "workflow-state.yaml").write_text(state_text, encoding="utf-8")
            for name, text in artifacts.items():
                (feature_dir / name).write_text(text, encoding="utf-8")
            args = SimpleNamespace(repo=str(repo), feature="demo", phase=phase)
            feature_docs.cmd_check(args)

    def state(self, frontend_branch="main", frontend_pc=None):
        return feature_docs.state_yaml(
            "demo",
            {"path": "/tmp/h5", "branch": frontend_branch, "commit": "abc"},
            {"path": "", "branch": "", "commit": ""},
            frontend_pc,
        )

    def test_check_passes(self):
        self.run_check("design", {"01-frontend-tech-design.md": "设计内容"}, self.state())

    def test_check_rejects_placeholder(self):
        with self.assertRaises(SystemExit):
            self.run_check("design", {"01-frontend-tech-design.md": "设计 TBD"}, self.state())

    def test_check_rejects_empty_file(self):
        with self.assertRaises(SystemExit):
            self.run_check("design", {"01-frontend-tech-design.md": "  "}, self.state())

    def test_check_rejects_missing_frontend_branch(self):
        with self.assertRaises(SystemExit):
            self.run_check(
                "design",
                {"01-frontend-tech-design.md": "设计内容"},
                self.state(frontend_branch=""),
            )

    def test_check_rejects_pc_path_without_branch(self):
        with self.assertRaises(SystemExit):
            self.run_check(
                "design",
                {"01-frontend-tech-design.md": "设计内容"},
                self.state(frontend_pc={"path": "/tmp/pc", "branch": "", "commit": ""}),
            )


if __name__ == "__main__":
    unittest.main()
