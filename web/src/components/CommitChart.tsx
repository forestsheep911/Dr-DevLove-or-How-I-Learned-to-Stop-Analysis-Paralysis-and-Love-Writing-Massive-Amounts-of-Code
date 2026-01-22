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
      <div className="mt-4 space-y-6">
        <div>
          <div className="text-sm text-gray-600 mb-2">提交数（单独刻度）</div>
          <AreaChart
            className="h-48"
            data={chartData}
            index="date"
            categories={["提交数"]}
            colors={["blue"]}
            valueFormatter={(value) => value.toLocaleString()}
            showLegend={false}
            showGridLines={true}
            showAnimation={true}
          />
        </div>
        <div>
          <div className="text-sm text-gray-600 mb-2">代码行变更（新增/删除）</div>
          <AreaChart
            className="h-48"
            data={chartData}
            index="date"
            categories={["新增行", "删除行"]}
            colors={["green", "red"]}
            valueFormatter={(value) => value.toLocaleString()}
            showLegend={true}
            showGridLines={true}
            showAnimation={true}
          />
        </div>
      </div>
    </Card>
  );
}
