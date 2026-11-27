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

    def run_context(self, skill_dir, repo):
        with patch.object(project_context, "SKILL_DIR", skill_dir):
            with patch.object(sys, "argv", ["project_context.py", "--repo", str(repo)]):
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


if __name__ == "__main__":
    unittest.main()
