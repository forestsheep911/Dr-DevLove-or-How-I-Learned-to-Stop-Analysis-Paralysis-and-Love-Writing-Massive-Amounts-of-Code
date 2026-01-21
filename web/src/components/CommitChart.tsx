"use client";

import { Card, Title, AreaChart } from "@tremor/react";
import { TimelineEntry } from "@/types/stats";

interface CommitChartProps {
  timeline: TimelineEntry[];
}

export function CommitChart({ timeline }: CommitChartProps) {
  // 按日期排序
  const sortedData = [...timeline].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // 格式化数据
  const chartData = sortedData.map((entry) => ({
    date: entry.date,
    提交数: entry.commits,
    新增行: entry.added,
    删除行: entry.deleted,
  }));

  return (
    <Card>
      <Title>提交趋势</Title>
      <AreaChart
        className="h-72 mt-4"
        data={chartData}
        index="date"
        categories={["提交数", "新增行", "删除行"]}
        colors={["blue", "green", "red"]}
        valueFormatter={(value) => value.toLocaleString()}
        showLegend={true}
        showGridLines={true}
        showAnimation={true}
      />
    </Card>
  );
}
