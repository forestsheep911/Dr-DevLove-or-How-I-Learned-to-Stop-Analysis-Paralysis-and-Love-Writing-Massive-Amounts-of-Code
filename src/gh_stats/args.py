#!/usr/bin/env python3
"""
参数解析模块 - 实现 CLI 声明式参数架构协议的诊断功能

根据 myrules.md 定义的 E-A-X-D 四维分类体系：
- E (Entity): 实体节点
- A (Attribute): 独立属性  
- X (Exclusion): 互斥约束
- D (Derivation): 推导规则
"""
import argparse
import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ValueSource(Enum):
    """参数值来源"""
    DEFAULT = "default"
    USER = "user"
    DERIVED = "derived"


class Entity(Enum):
    """实体节点 (E) 定义"""
    E_USER = "E_USER"           # 用户相关参数
    E_DISCOVERY = "E_DISCOVERY"  # 仓库发现相关
    E_DATE = "E_DATE"           # 日期范围相关
    E_EXPORT = "E_EXPORT"       # 导出相关
    E_ORG_SUMMARY = "E_ORG_SUMMARY"  # 组织汇总模式
    E_ARENA = "E_ARENA"         # 竞技场/排名相关
    E_DISPLAY = "E_DISPLAY"     # 显示/输出相关


@dataclass
class ParamMeta:
    """单个参数的元信息"""
    name: str
    value: Any
    source: ValueSource
    entity: Entity
    raw_input: Optional[str] = None  # 用户原始输入（如 "today-1week"）
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        result = {
            "value": self.value if self.value is not None else "null",
            "source": self.source.value,
            "entity": self.entity.value,
        }
        if self.raw_input and self.raw_input != str(self.value):
            result["source"] = f'{self.source.value} (parsed from "{self.raw_input}")'
        if self.errors:
            result["errors"] = self.errors
        return result


@dataclass
class ParseResult:
    """完整解析结果"""
    params: Dict[str, ParamMeta] = field(default_factory=dict)
    active_entities: List[Tuple[Entity, str]] = field(default_factory=list)  # (entity, activated_by)
    exclusion_violations: List[str] = field(default_factory=list)
    dependency_errors: List[str] = field(default_factory=list)
    pending_interactions: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        return not self.exclusion_violations and not self.dependency_errors
    
    @property
    def error_count(self) -> int:
        return len(self.exclusion_violations) + len(self.dependency_errors)


# 参数到实体的映射表 (A -> E)
PARAM_ENTITY_MAP = {
    # E_USER
    "user": Entity.E_USER,
    
    # E_DISCOVERY
    "personal": Entity.E_DISCOVERY,
    "orgs": Entity.E_DISCOVERY,
    "personal_limit": Entity.E_DISCOVERY,
    "org_limit": Entity.E_DISCOVERY,
    "all_branches": Entity.E_DISCOVERY,
    
    # E_DATE
    "since": Entity.E_DATE,
    "until": Entity.E_DATE,
    "range": Entity.E_DATE,
    
    # E_EXPORT
    "export_commits": Entity.E_EXPORT,
    "full_message": Entity.E_EXPORT,
    "output": Entity.E_EXPORT,
    
    # E_ORG_SUMMARY
    "org_summary": Entity.E_ORG_SUMMARY,
    
    # E_ARENA
    "arena": Entity.E_ARENA,
    "arena_top": Entity.E_ARENA,
    
    # E_DISPLAY
    "highlights": Entity.E_DISPLAY,
    "dry_run": Entity.E_DISPLAY,
    "exclude_noise": Entity.E_DISPLAY,
    "dev": Entity.E_DISPLAY,
}

# 参数默认值表
PARAM_DEFAULTS = {
    "user": None,
    "personal": True,
    "orgs": "",
    "since": None,
    "until": None,
    "range": None,
    "personal_limit": None,
    "org_limit": None,
    "all_branches": False,
    "export_commits": False,
    "full_message": False,
    "output": None,
    "org_summary": None,
    "arena": False,
    "arena_top": 5,
    "highlights": False,
    "dry_run": False,
    "exclude_noise": False,
    "dev": False,
}


def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(description="GitHub contribution statistics")
    parser.add_argument('--user', type=str, help='Target GitHub username (defaults to authenticated user)')
    parser.add_argument('--personal', dest='personal', action='store_true', default=True, help='Include personal repos (default)')
    parser.add_argument('--no-personal', dest='personal', action='store_false', help='Exclude personal repos')
    parser.add_argument('--orgs', type=str, default='', help='Comma-separated organization names')
    
    # Date selection (yt-dlp style aliases)
    parser.add_argument('--since', '--date-after', dest='since', type=str, help='Start date (YYYY-MM-DD, YYYYMMDD, or relative like "today-1week")')
    parser.add_argument('--until', '--date-before', dest='until', type=str, help='End date (YYYY-MM-DD, YYYYMMDD, or relative like "today")')
    
    parser.add_argument('--range', type=str, help='Date range preset (e.g., today, week, 3days)')
    parser.add_argument('--personal-limit', type=int, help='Max personal repos to scan (0=unlimited)')
    parser.add_argument('--org-limit', type=int, help='Max repos per org to scan (0=unlimited)')
    parser.add_argument('--all-branches', action='store_true', help='Scan all active branches (found via Events API) instead of just default branch')
    parser.add_argument('--export-commits', action='store_true', help='Export commit messages to a Markdown file')
    parser.add_argument('--full-message', action='store_true', help='Include full commit message body in export')
    parser.add_argument('--output', '-o', type=str, help='Specify output filename for export')
    parser.add_argument('--org-summary', type=str, metavar='ORG', help='Org summary mode: analyze a single organization (mutually exclusive with --orgs)')
    parser.add_argument('--arena', action='store_true', help='Show competition rankings (requires --org-summary)')
    parser.add_argument('--arena-top', type=int, default=5, metavar='N', help='Number of top contributors to show in arena rankings (0=all, default=5)')
    parser.add_argument('--highlights', action='store_true', help='Show insights like longest streak and most productive day')
    parser.add_argument('--exclude-noise', action='store_true', help='Exclude noisy files like lockfiles and generated artifacts')
    parser.add_argument('--dry-run', action='store_true', help='Show parameter diagnostics without executing')
    parser.add_argument('--dev', action='store_true', help='Enable development diagnostic mode: print command, parsing details, and errors before execution')
    
    return parser


def parse_with_diagnostics(argv: Optional[List[str]] = None) -> Tuple[argparse.Namespace, ParseResult]:
    """
    解析参数并生成诊断信息
    
    Args:
        argv: 命令行参数列表，None 表示使用 sys.argv
        
    Returns:
        (args, result): 解析后的参数对象和诊断结果
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    result = ParseResult()
    
    # 追踪每个参数的状态
    for param_name, entity in PARAM_ENTITY_MAP.items():
        value = getattr(args, param_name, None)
        default = PARAM_DEFAULTS.get(param_name)
        
        # 判断值来源
        if value == default:
            source = ValueSource.DEFAULT
        else:
            source = ValueSource.USER
            # 记录激活的实体
            if entity not in [e for e, _ in result.active_entities]:
                result.active_entities.append((entity, f"--{param_name.replace('_', '-')}"))
        
        # 创建参数元数据
        meta = ParamMeta(
            name=f"--{param_name.replace('_', '-')}",
            value=value,
            source=source,
            entity=entity,
        )
        result.params[param_name] = meta
    
    # 推导规则 (D): --arena-top 非默认值时激活 --arena
    if args.arena_top != 5 and not args.arena:
        result.params["arena"].source = ValueSource.DERIVED
        result.params["arena"].value = True
        args.arena = True
        if Entity.E_ARENA not in [e for e, _ in result.active_entities]:
            result.active_entities.append((Entity.E_ARENA, "--arena-top (derived)"))
    
    # 互斥约束检查 (X): --org-summary 与 --orgs
    orgs = [o.strip() for o in args.orgs.split(',') if o.strip()]
    if args.org_summary and orgs:
        result.exclusion_violations.append(
            "EXCLUSION_CONFLICT: --org-summary and --orgs are mutually exclusive"
        )
    
    # 依赖检查: --arena 需要 --org-summary
    if args.arena and not args.org_summary:
        result.dependency_errors.append(
            "DEPENDENCY_MISSING: --arena requires --org-summary"
        )
    
    return args, result


def format_diagnostics(result: ParseResult) -> str:
    """
    格式化诊断输出
    
    Args:
        result: 解析结果
        
    Returns:
        格式化的诊断字符串
    """
    lines = []
    lines.append("=== DRY RUN DIAGNOSTICS ===")
    lines.append("")
    
    # [Parameters]
    lines.append("[Parameters]")
    for param_name, meta in sorted(result.params.items()):
        lines.append(f"  {meta.name}:")
        info = meta.to_dict()
        lines.append(f"    value: {info['value']}")
        lines.append(f"    source: {info['source']}")
        lines.append(f"    entity: {info['entity']}")
        if "errors" in info:
            for err in info["errors"]:
                lines.append(f"    error: {err}")
        lines.append("")
    
    # [Active Entities]
    lines.append("[Active Entities]")
    if result.active_entities:
        for entity, activated_by in result.active_entities:
            lines.append(f"  - {entity.value} (activated by: {activated_by})")
    else:
        lines.append("  (none - all parameters at default)")
    lines.append("")
    
    # [Errors]
    lines.append("[Errors]")
    all_errors = result.exclusion_violations + result.dependency_errors
    if all_errors:
        for err in all_errors:
            lines.append(f"  [X] {err}")
    else:
        lines.append("  (none)")
    lines.append("")
    
    # [Pending Interactions]
    lines.append("[Pending Interactions]")
    if result.pending_interactions:
        for interaction in result.pending_interactions:
            lines.append(f"  [!] {interaction}")
    else:
        lines.append("  (none)")
    lines.append("")
    
    # [Validation Result]
    lines.append("[Validation Result]")
    if result.is_valid:
        lines.append("  [OK] VALID - Ready to execute")
    else:
        lines.append(f"  [X] INVALID - {result.error_count} error(s) found")
    
    return "\n".join(lines)
