#!/usr/bin/env python3
"""
测试 args.py 模块
"""
import pytest
from gh_stats.args import (
    parse_with_diagnostics,
    format_diagnostics,
    ValueSource,
    Entity,
)


class TestDefaultValues:
    """测试默认值"""
    
    def test_all_defaults(self):
        """无参数时所有值应为默认"""
        args, result = parse_with_diagnostics(["--dry-run"])
        
        # 验证 dry-run 是用户提供的
        assert result.params["dry_run"].source == ValueSource.USER
        
        # 验证其他参数是默认的
        assert result.params["user"].source == ValueSource.DEFAULT
        assert result.params["orgs"].source == ValueSource.DEFAULT
        assert result.params["arena"].source == ValueSource.DEFAULT
    
    def test_validation_passes_with_defaults(self):
        """默认参数应该通过验证"""
        _, result = parse_with_diagnostics(["--dry-run"])
        assert result.is_valid
        assert result.error_count == 0


class TestUserProvidedValues:
    """测试用户提供的值"""
    
    def test_user_value_detected(self):
        """用户提供的值应被正确标记"""
        _, result = parse_with_diagnostics(["--dry-run", "--orgs=google"])
        
        assert result.params["orgs"].value == "google"
        assert result.params["orgs"].source == ValueSource.USER
    
    def test_active_entities_tracked(self):
        """激活的实体应被追踪"""
        _, result = parse_with_diagnostics(["--dry-run", "--since=today-1week"])
        
        entities = [e for e, _ in result.active_entities]
        assert Entity.E_DATE in entities


class TestDerivedValues:
    """测试推导规则"""
    
    def test_arena_top_derives_arena(self):
        """--arena-top 非默认值应推导出 --arena"""
        args, result = parse_with_diagnostics(["--dry-run", "--arena-top=10", "--org-summary=test"])
        
        assert args.arena == True
        assert result.params["arena"].source == ValueSource.DERIVED


class TestExclusionViolations:
    """测试互斥约束"""
    
    def test_org_summary_orgs_exclusive(self):
        """--org-summary 和 --orgs 应互斥"""
        _, result = parse_with_diagnostics([
            "--dry-run", "--org-summary=google", "--orgs=microsoft"
        ])
        
        assert not result.is_valid
        assert len(result.exclusion_violations) == 1
        assert "mutually exclusive" in result.exclusion_violations[0]


class TestDependencyChecks:
    """测试依赖检查"""
    
    def test_arena_requires_org_summary(self):
        """--arena 应该需要 --org-summary"""
        _, result = parse_with_diagnostics(["--dry-run", "--arena"])
        
        assert not result.is_valid
        assert len(result.dependency_errors) == 1
        assert "--arena requires --org-summary" in result.dependency_errors[0]
    
    def test_arena_with_org_summary_valid(self):
        """--arena 与 --org-summary 一起使用应通过"""
        _, result = parse_with_diagnostics([
            "--dry-run", "--arena", "--org-summary=google"
        ])
        
        assert result.is_valid


class TestFormatDiagnostics:
    """测试诊断输出格式"""
    
    def test_output_contains_sections(self):
        """输出应包含所有主要部分"""
        _, result = parse_with_diagnostics(["--dry-run"])
        output = format_diagnostics(result)
        
        assert "=== DRY RUN DIAGNOSTICS ===" in output
        assert "[Parameters]" in output
        assert "[Active Entities]" in output
        assert "[Errors]" in output
        assert "[Pending Interactions]" in output
        assert "[Validation Result]" in output
    
    def test_error_output_format(self):
        """错误应正确显示"""
        _, result = parse_with_diagnostics(["--dry-run", "--arena"])
        output = format_diagnostics(result)
        
        assert "❌ DEPENDENCY_MISSING" in output
        assert "INVALID" in output
