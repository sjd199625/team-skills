import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = (
    Path(__file__).parents[1]
    / ".agents"
    / "skills"
    / "frontend-workflow"
    / "scripts"
    / "project_context.py"
)
SPEC = importlib.util.spec_from_file_location("project_context", SCRIPT)
project_context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project_context)


class ProfileReferenceTests(unittest.TestCase):
    def make_repo(self, root):
        repo = root / "repo"
        repo.mkdir()
        (repo / "package.json").write_text(
            json.dumps({"name": "demo", "scripts": {}}),
            encoding="utf-8",
        )
        return repo

    def run_context(self, skill_dir, repo, *extra):
        argv = ["project_context.py", "--repo", str(repo), *extra]
        with patch.object(project_context, "SKILL_DIR", skill_dir):
            with patch.object(sys, "argv", argv):
                output = io.StringIO()
                with patch("sys.stdout", output):
                    project_context.main()
        return output.getvalue()

    def test_prefers_local_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            references = root / "skill" / "references"
            references.mkdir(parents=True)
            (references / "project-profile.md").write_text("template", encoding="utf-8")
            (references / "project-profile.local.md").write_text("local", encoding="utf-8")
            output = self.run_context(root / "skill", self.make_repo(root))
        self.assertIn("references/project-profile.local.md", output)

    def test_falls_back_to_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            references = root / "skill" / "references"
            references.mkdir(parents=True)
            (references / "project-profile.md").write_text("template", encoding="utf-8")
            output = self.run_context(root / "skill", self.make_repo(root))
        self.assertIn("references/project-profile.md", output)
        self.assertNotIn("project-profile.local.md", output)

    def test_feature_files_match_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            references = root / "skill" / "references"
            references.mkdir(parents=True)
            (references / "project-profile.md").write_text("template", encoding="utf-8")
            repo = self.make_repo(root)
            (repo / "src" / "KeyBox").mkdir(parents=True)
            (repo / "src" / "KeyBox" / "KeyList.tsx").write_text("", encoding="utf-8")
            (repo / "src" / "Store").mkdir(parents=True)
            (repo / "src" / "Store" / "StoreList.tsx").write_text("", encoding="utf-8")
            (repo / "docs" / "key-box").mkdir(parents=True)
            (repo / "docs" / "key-box" / "01-frontend-tech-design.md").write_text("", encoding="utf-8")
            output = self.run_context(root / "skill", repo, "--feature", "key-box")
        self.assertIn("feature_dir: present", output)
        self.assertIn("src/KeyBox/KeyList.tsx", output)
        self.assertNotIn("StoreList.tsx", output)

    def test_missing_feature_dir_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            references = root / "skill" / "references"
            references.mkdir(parents=True)
            (references / "project-profile.md").write_text("template", encoding="utf-8")
            output = self.run_context(root / "skill", self.make_repo(root), "--feature", "absent")
        self.assertIn("feature_dir: missing", output)
        self.assertIn("feature_files:", output)
        self.assertIn("  -", output)
        self.assertNotIn("KeyList", output)


if __name__ == "__main__":
    unittest.main()
