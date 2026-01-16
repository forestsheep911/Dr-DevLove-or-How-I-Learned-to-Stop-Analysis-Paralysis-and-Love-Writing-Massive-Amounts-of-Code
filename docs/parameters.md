# gh-stats 参数规格文档

基于 [CLI 声明式参数架构协议](./myrules.md) 整理。

---

## 实体层级结构 (Entity Hierarchy)

```
gh-stats
├── E_USER          # 用户身份
├── E_DISCOVERY     # 仓库发现
├── E_DATE          # 日期范围
├── E_EXPORT        # 导出控制
├── E_ORG_SUMMARY   # 组织汇总模式
│   └── E_ARENA     # 竞技场排名 (依赖 E_ORG_SUMMARY)
└── E_DISPLAY       # 显示控制
```

---

## 参数详细规格

### E_USER - 用户身份

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--user` | string | (当前认证用户) | GitHub 用户名 | 目标分析用户 |

---

### E_DISCOVERY - 仓库发现

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--personal` / `--no-personal` | bool | `true` | `true` \| `false` | 是否包含个人仓库 |
| `--orgs` | string | `""` | 逗号分隔的组织名 | 要分析的组织列表 |
| `--personal-limit` | int | `null` | ≥0 (0=无限制) | 个人仓库扫描上限 |
| `--org-limit` | int | `null` | ≥0 (0=无限制) | 每个组织仓库扫描上限 |
| `--all-branches` | flag | `false` | - | 扫描所有活跃分支 |

---

### E_DATE - 日期范围

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--since` | string | `today` | 日期格式 (见下) | 开始日期 |
| `--until` | string | `today` | 日期格式 (见下) | 结束日期 |
| `--range` | string | `null` | 预设值 (见下) | 日期范围预设 |

**日期格式**:
- 绝对: `YYYY-MM-DD`, `YYYYMMDD`
- 相对: `today`, `today-1week`, `today-3days`

**Range 预设值**:
- `today` — 今天
- `week` — 本周
- `month` — 本月
- `3days`, `7days`, `30days` — 最近 N 天

---

### E_EXPORT - 导出控制

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--export-commits` | flag | `false` | - | 导出 commit 消息 |
| `--full-message` | flag | `false` | - | 包含完整 commit body |
| `--output`, `-o` | string | `null` | 文件路径 | 输出文件名 |

---

### E_ORG_SUMMARY - 组织汇总模式

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--org-summary` | string | `null` | 组织名 | 启用组织汇总模式 |

---

### E_ARENA - 竞技场排名

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--arena` | flag | `false` | - | 显示竞争排名 |
| `--arena-top` | int | `5` | ≥0 (0=全部) | 排名显示人数 |

**依赖关系**: `--arena` 需要 `--org-summary`

**推导规则 (D)**: `--arena-top` 非默认值时自动激活 `--arena`

---

### E_DISPLAY - 显示控制

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
|-----|------|--------|---------|------|
| `--highlights` | flag | `false` | - | 显示亮点摘要 |
| `--exclude-noise` | flag | `false` | - | 排除 lockfile 与生成物等杂质文件 |
| `--dry-run` | flag | `false` | - | 诊断模式 |

---

## 互斥约束 (X - Exclusions)

| 约束 ID | 互斥参数组 | 说明 |
|--------|-----------|------|
| X001 | `--org-summary` ⟷ `--orgs` | 组织汇总模式与多组织模式互斥 |

---

## 推导规则 (D - Derivations)

| 规则 ID | 触发条件 | 推导结果 |
|--------|---------|---------|
| D001 | `--arena-top` ≠ 5 | 自动设置 `--arena = true` |

---

## 依赖关系

```
--arena ──requires──> --org-summary
```

---

## 类型说明

| 类型 | 格式 | 示例 |
|-----|------|------|
| `flag` | 布尔开关 | `--arena` |
| `string` | 字符串 | `--user=octocat` |
| `int` | 整数 | `--arena-top=10` |
