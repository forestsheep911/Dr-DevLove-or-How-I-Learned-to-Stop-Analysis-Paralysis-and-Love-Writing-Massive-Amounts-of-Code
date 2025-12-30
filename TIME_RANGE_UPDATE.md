# 时间范围参数改进总结

## 改进内容

根据您的要求，已将时间范围参数更新为更符合实际语言习惯的表达方式。

## 新增支持的参数

### 当前时间范围
- `thisweek` - 本周（从周一到今天）
- `thismonth` - 本月（从1号到今天）
- `thisyear` - 本年（从1月1日到今天）

### 历史时间范围
- `yesterday` - 昨天
- `lastweek` - 上周（完整的一周，周一到周日）
- `lastmonth` - 上月（完整的一个月）
- `lastyear` - 去年（完整的一年）

## 向后兼容

为保持向后兼容性，原有的参数仍然可用：
- `today` → 今天
- `week` → 等同于 `thisweek`（本周）
- `month` → 等同于 `thismonth`（本月）
- `year` → 等同于 `thisyear`（本年）

## 修改的文件

1. **src/gh_stats/utils.py**
   - 更新 `parse_date_range()` 函数
   - 添加对所有新时间范围参数的支持
   - 包含详细的中文注释说明每个参数的含义

2. **src/gh_stats/main.py**
   - 更新 `defaults_map` 字典，为新参数配置合适的扫描限制
   - 更新活跃分支检测逻辑，支持 `yesterday` 和 `thisweek`

3. **README.zh-CN.md**
   - 更新特性说明，展示所有新参数
   - 更新使用示例，使用新的参数格式
   - 更新参数表格，列出所有支持的参数
   - 新增"常用时间范围表达"部分，详细说明各参数的用法

## 使用示例

```bash
# 查看今天的统计
poetry run gh-stats --range today

# 查看昨天的工作
poetry run gh-stats --range yesterday

# 查看本周的统计
poetry run gh-stats --range thisweek

# 查看上周的统计（完整一周）
poetry run gh-stats --range lastweek

# 查看本月的统计
poetry run gh-stats --range thismonth

# 查看上月的统计（完整一月）
poetry run gh-stats --range lastmonth

# 查看本年的统计
poetry run gh-stats --range thisyear

# 查看去年的统计（完整一年）
poetry run gh-stats --range lastyear
```

## 测试验证

已创建测试脚本 `test_time_ranges.py`，验证所有新参数的正确性。
测试结果：**全部通过** ✓

- 测试用例：11个
- 成功：11个
- 失败：0个

## 实现细节

### 时间计算逻辑

1. **yesterday（昨天）**
   - 返回：昨天到昨天

2. **thisweek（本周）**
   - 返回：本周周一到今天

3. **lastweek（上周）**
   - 返回：上周周一到上周周日

4. **thismonth（本月）**
   - 返回：本月1号到今天

5. **lastmonth（上月）**
   - 返回：上月1号到上月最后一天

6. **thisyear（本年）**
   - 返回：本年1月1日到今天

7. **lastyear（去年）**
   - 返回：去年1月1日到去年12月31日

所有实现都考虑了边界情况（如月末、年末等），确保计算准确。
