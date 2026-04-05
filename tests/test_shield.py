"""
Shield CLI — Unit Tests
Run with: python -m pytest tests/ -v
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════
# Input Validation Tests
# ═══════════════════════════════════════════════════════════════

class TestInputValidation:
    """Test command injection prevention and target validation."""

    def setup_method(self):
        from utils.input_validator import validate_target
        self.validate = validate_target

    # ── Valid Targets ─────────────────────────────────────────
    def test_valid_hostname(self):
        assert self.validate("example.com")[0] is True

    def test_valid_subdomain(self):
        assert self.validate("sub.example.com")[0] is True

    def test_valid_ipv4(self):
        assert self.validate("192.168.1.1")[0] is True

    def test_valid_ipv4_cidr(self):
        assert self.validate("10.0.0.0/24")[0] is True

    def test_valid_url_http(self):
        assert self.validate("http://example.com")[0] is True

    def test_valid_url_https(self):
        assert self.validate("https://example.com/path")[0] is True

    def test_valid_nmap_target(self):
        assert self.validate("scanme.nmap.org")[0] is True

    # ── Command Injection Prevention ─────────────────────────
    def test_reject_semicolon_injection(self):
        assert self.validate("example.com; rm -rf /")[0] is False

    def test_reject_pipe_injection(self):
        assert self.validate("example.com | cat /etc/passwd")[0] is False

    def test_reject_backtick_injection(self):
        assert self.validate("`whoami`.evil.com")[0] is False

    def test_reject_dollar_injection(self):
        assert self.validate("$(whoami).evil.com")[0] is False

    def test_reject_ampersand_injection(self):
        assert self.validate("example.com && malicious")[0] is False

    def test_reject_quotes_injection(self):
        assert self.validate("example.com' OR '1'='1")[0] is False

    # ── Invalid Inputs ───────────────────────────────────────
    def test_reject_empty(self):
        assert self.validate("")[0] is False

    def test_reject_spaces_only(self):
        assert self.validate("   ")[0] is False

    def test_reject_too_long(self):
        assert self.validate("a" * 254 + ".com")[0] is False


# ═══════════════════════════════════════════════════════════════
# Scope Validation Tests
# ═══════════════════════════════════════════════════════════════

class TestScopeValidation:
    """Test that private networks are blocked."""

    def setup_method(self):
        from utils.scope_validator import ScopeValidator
        self.sv = ScopeValidator({
            "scope": {
                "blacklist": [
                    "127.0.0.0/8", "10.0.0.0/8",
                    "172.16.0.0/12", "192.168.0.0/16"
                ]
            }
        })

    def test_allow_public_domain(self):
        valid, _ = self.sv.validate_target("scanme.nmap.org")
        assert valid is True

    def test_allow_public_url(self):
        valid, _ = self.sv.validate_target("https://example.com")
        assert valid is True

    def test_block_localhost(self):
        valid, _ = self.sv.validate_target("127.0.0.1")
        assert valid is False

    def test_block_private_10(self):
        valid, _ = self.sv.validate_target("10.0.0.1")
        assert valid is False

    def test_block_private_172(self):
        valid, _ = self.sv.validate_target("172.16.0.1")
        assert valid is False

    def test_block_private_192(self):
        valid, _ = self.sv.validate_target("192.168.1.1")
        assert valid is False


# ═══════════════════════════════════════════════════════════════
# Memory System Tests
# ═══════════════════════════════════════════════════════════════

class TestMemorySystem:
    """Test pentest state management."""

    def setup_method(self):
        from core.memory import PentestMemory, Finding
        self.Finding = Finding
        self.mem = PentestMemory("example.com")

    def test_session_id_generated(self):
        assert self.mem.session_id is not None
        assert len(self.mem.session_id) > 0

    def test_add_finding(self):
        f = self.Finding(
            id="t1", severity="high", title="Test Finding",
            description="Test", evidence="test", tool="nmap",
            target="example.com", timestamp="2026-01-01T00:00:00",
            remediation="Fix it",
        )
        self.mem.add_finding(f)
        assert len(self.mem.findings) == 1

    def test_findings_summary(self):
        for sev in ["critical", "high", "medium", "low"]:
            self.mem.add_finding(self.Finding(
                id=f"t_{sev}", severity=sev, title=f"{sev} issue",
                description="d", evidence="e", tool="t",
                target="example.com", timestamp="2026-01-01T00:00:00",
                remediation="r",
            ))
        summary = self.mem.get_findings_summary()
        assert isinstance(summary, dict)
        assert summary.get("critical", 0) == 1
        assert summary.get("high", 0) == 1

    def test_context_for_ai(self):
        ctx = self.mem.get_context_for_ai()
        assert isinstance(ctx, str)


# ═══════════════════════════════════════════════════════════════
# Config Loading Tests
# ═══════════════════════════════════════════════════════════════

class TestConfigLoading:
    """Test configuration file loading."""

    def test_config_exists(self):
        assert os.path.exists("config/shield.yaml")

    def test_config_loads(self):
        import yaml
        with open("config/shield.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        assert "ai" in config
        assert "pentest" in config
        assert "scope" in config

    def test_safe_mode_default_on(self):
        import yaml
        with open("config/shield.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        assert config["pentest"]["safe_mode"] is True

    def test_blacklist_has_private_ranges(self):
        import yaml
        with open("config/shield.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        bl = config["scope"]["blacklist"]
        assert "192.168.0.0/16" in bl
        assert "10.0.0.0/8" in bl


# ═══════════════════════════════════════════════════════════════
# Workflow Loading Tests
# ═══════════════════════════════════════════════════════════════

class TestWorkflows:
    """Test workflow YAML loading."""

    def test_all_workflows_exist(self):
        workflows = ["recon", "web_pentest", "network", "autonomous", "quick_scan", "full_scan"]
        for wf in workflows:
            assert os.path.exists(f"workflows/{wf}.yaml"), f"Missing: {wf}.yaml"

    def test_workflow_has_steps(self):
        import yaml
        with open("workflows/recon.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "steps" in data
        assert len(data["steps"]) > 0

    def test_full_scan_has_all_tools(self):
        import yaml
        with open("workflows/full_scan.yaml", "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tool_steps = [s for s in data["steps"] if s.get("type") == "tool"]
        assert len(tool_steps) == 19, f"Expected 19 tool steps, got {len(tool_steps)}"


# ═══════════════════════════════════════════════════════════════
# Tool Agent Safety Tests
# ═══════════════════════════════════════════════════════════════

class TestToolSafety:
    """Test safe mode restrictions."""

    def test_block_sqlmap_high_risk(self):
        from core.tool_agent import ToolAgent
        config = {"pentest": {"safe_mode": True}}

        class FakeClient:
            pass
        class FakeMemory:
            target = "example.com"

        agent = ToolAgent.__new__(ToolAgent)
        agent.config = config
        assert agent._is_unsafe_params("sqlmap", {"risk": 3}) is True

    def test_allow_sqlmap_low_risk(self):
        from core.tool_agent import ToolAgent
        config = {"pentest": {"safe_mode": True}}
        agent = ToolAgent.__new__(ToolAgent)
        agent.config = config
        assert agent._is_unsafe_params("sqlmap", {"risk": 1}) is False

    def test_safe_mode_off_allows_all(self):
        from core.tool_agent import ToolAgent
        config = {"pentest": {"safe_mode": False}}
        agent = ToolAgent.__new__(ToolAgent)
        agent.config = config
        assert agent._is_unsafe_params("sqlmap", {"risk": 3}) is False
