"""Tests for RuleHawk Validators"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules.validators import (
    check_branch_protection,
    check_ci_status,
    check_environment,
    check_task_plan,
    check_task_plan_updated,
    run_security_phase,
)


class TestValidators(unittest.TestCase):
    """Test validator functions"""

    @patch("subprocess.run")
    def test_check_branch_protection_on_main(self, mock_run):
        """Test branch protection fails on main branch"""
        mock_run.return_value = Mock(stdout="main\n", stderr="", returncode=0)

        result = check_branch_protection({})

        self.assertFalse(result["success"])
        self.assertIn("protected branch", result["message"])
        self.assertIn("main", result["message"])

    @patch("subprocess.run")
    def test_check_branch_protection_on_feature(self, mock_run):
        """Test branch protection passes on feature branch"""
        mock_run.return_value = Mock(stdout="feature/new-feature\n", stderr="", returncode=0)

        result = check_branch_protection({})

        self.assertTrue(result["success"])
        self.assertIn("feature/new-feature", result["message"])

    @patch("subprocess.run")
    def test_check_branch_protection_error(self, mock_run):
        """Test branch protection handles errors gracefully"""
        mock_run.side_effect = Exception("Git error")

        result = check_branch_protection({})

        self.assertFalse(result["success"])
        self.assertIn("Could not determine", result["message"])

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_check_environment_clean_git(self, mock_exists, mock_run):
        """Test environment check with clean git status"""
        mock_run.return_value = Mock(stdout="", stderr="", returncode=0)
        mock_exists.return_value = False  # No package.json or requirements.txt

        result = check_environment({})

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Environment ready")

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_check_environment_uncommitted_changes(self, mock_exists, mock_run):
        """Test environment check with uncommitted changes"""
        mock_run.return_value = Mock(stdout="M file1.py\nA file2.py\n", stderr="", returncode=0)
        mock_exists.return_value = False

        result = check_environment({})

        self.assertFalse(result["success"])
        self.assertIn("uncommitted changes", result["details"][0])

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_check_task_plan_exists_and_complete(self, mock_read, mock_exists):
        """Test task plan check when file exists with all sections"""
        mock_exists.return_value = True
        mock_read.return_value = """
## Objective
Build awesome feature

## Implementation Steps
- [ ] Step 1
- [ ] Step 2

## Current Status
Working on step 1
"""

        result = check_task_plan({})

        self.assertTrue(result["success"])
        self.assertIn("complete", result["message"])

    @patch("pathlib.Path.exists")
    def test_check_task_plan_missing(self, mock_exists):
        """Test task plan check when file is missing"""
        mock_exists.return_value = False

        result = check_task_plan({})

        self.assertFalse(result["success"])
        self.assertIn("No task plan found", result["message"])
        self.assertTrue(len(result["details"]) > 0)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_check_task_plan_incomplete(self, mock_read, mock_exists):
        """Test task plan check when file is missing sections"""
        mock_exists.return_value = True
        mock_read.return_value = """
## Objective
Build feature

Missing other sections
"""

        result = check_task_plan({})

        self.assertFalse(result["success"])
        self.assertIn("incomplete", result["message"])
        self.assertIn("## Implementation Steps", result["details"][0])

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_check_task_plan_updated_recently(self, mock_stat, mock_exists):
        """Test task plan update check when recently modified"""
        import time

        mock_exists.return_value = True
        mock_stat.return_value = Mock(st_mtime=time.time() - 3600)  # 1 hour ago

        result = check_task_plan_updated({})

        self.assertTrue(result["success"])
        self.assertIn("recently updated", result["message"])

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_check_task_plan_updated_stale(self, mock_stat, mock_exists):
        """Test task plan update check when stale"""
        import time

        mock_exists.return_value = True
        mock_stat.return_value = Mock(st_mtime=time.time() - 10800)  # 3 hours ago

        result = check_task_plan_updated({})

        self.assertFalse(result["success"])
        self.assertIn("not updated recently", result["message"])

    @patch("subprocess.run")
    def test_check_ci_status_with_github_actions(self, mock_run):
        """Test CI status check with GitHub Actions configured"""
        mock_run.return_value = Mock(returncode=0)  # Tests pass

        # Mock the Path operations
        with patch("pathlib.Path.is_dir", return_value=True):
            with patch("pathlib.Path.exists", return_value=True):
                result = check_ci_status({})

        self.assertTrue(result["success"])

    @patch("pathlib.Path.exists")
    def test_check_ci_status_no_ci(self, mock_exists):
        """Test CI status check with no CI configured"""
        mock_exists.return_value = False

        result = check_ci_status({})

        self.assertFalse(result["success"])
        self.assertIn("No CI configuration", result["message"])

    @patch("subprocess.run")
    def test_run_security_phase_clean(self, mock_run):
        """Test security phase with no issues"""
        mock_run.return_value = Mock(stdout="All clear - no issues found", stderr="", returncode=0)

        result = run_security_phase({})

        self.assertTrue(result["success"])
        self.assertIn("passed", result["message"])

    @patch("subprocess.run")
    def test_run_security_phase_with_issues(self, mock_run):
        """Test security phase with security issues"""
        mock_run.return_value = Mock(stdout="Found 2 leaks with 3 secrets", stderr="", returncode=1)

        result = run_security_phase({})

        self.assertFalse(result["success"])
        self.assertIn("Security issues detected", result["message"])


if __name__ == "__main__":
    unittest.main()
