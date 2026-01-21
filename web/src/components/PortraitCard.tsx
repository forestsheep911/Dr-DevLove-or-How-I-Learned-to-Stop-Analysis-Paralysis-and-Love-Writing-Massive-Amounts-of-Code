"use client";

import { Card, Title, BarChart, Flex, Text, Metric, Divider } from "@tremor/react";
import { Portrait, WEEKDAY_NAMES } from "@/types/stats";

interface PortraitCardProps {
  portrait: Portrait;
}

export function PortraitCard({ portrait }: PortraitCardProps) {
  // 工作日统计
  const weekdayData = WEEKDAY_NAMES.map((day, index) => ({
    day,
    提交数: portrait.weekdayStats[index] || 0,
  }));

  // 小时统计 - 只显示有数据的时段
  const hourData = Object.entries(portrait.hourStats)
    .map(([hour, count]) => ({
      hour: `${hour}:00`,
      提交数: count,
    }))
    .filter((d) => d.提交数 > 0)
    .sort((a, b) => parseInt(a.hour) - parseInt(b.hour));

  // 找出高峰时段
  const peakHour = Object.entries(portrait.hourStats).sort(
    ([, a], [, b]) => b - a
  )[0];

  return (
    <Card>
      <Title>开发者画像</Title>

      {/* 关键指标 */}
      <Flex className="mt-4 space-x-4">
        <div className="text-center">
          <Text>平均每次提交</Text>
          <Metric>{portrait.avgLinesPerCommit.toFixed(1)}</Metric>
          <Text className="text-gray-500">行代码</Text>
        </div>
        {peakHour && (
          <div className="text-center">
            <Text>高峰编码时段</Text>
            <Metric>{peakHour[0]}:00</Metric>
            <Text className="text-gray-500">{peakHour[1]} 次提交</Text>
          </div>
        )}
      </Flex>

      <Divider />

      {/* 工作日分布 */}
      <Text className="font-medium mb-2">工作日节奏</Text>
      <BarChart
        className="h-40"
        data={weekdayData}
        index="day"
        categories={["提交数"]}
        colors={["blue"]}
        showLegend={false}
        showAnimation={true}
      />

      {/* 仓库冠军 */}
      {portrait.repoChampions && (
        <>
          <Divider />
          <Text className="font-medium mb-2">仓库画像</Text>
          <div className="space-y-2">
            {portrait.repoChampions.growth && (
              <Flex>
                <Text>🌱 增长冠军</Text>
                <Text>
                  <span className="font-medium">
                    {portrait.repoChampions.growth.name.split("/").pop()}
                  </span>
                  <span className="text-green-600 ml-2">
                    +{portrait.repoChampions.growth.value.toLocaleString()}
                  </span>
                </Text>
              </Flex>
            )}
            {portrait.repoChampions.refactor && (
              <Flex>
                <Text>🔧 重构冠军</Text>
                <Text>
                  <span className="font-medium">
                    {portrait.repoChampions.refactor.name.split("/").pop()}
                  </span>
                  <span className="text-blue-600 ml-2">
                    {portrait.repoChampions.refactor.value.toLocaleString()} 行变更
                  </span>
                </Text>
              </Flex>
            )}
            {portrait.repoChampions.slimming && (
              <Flex>
                <Text>✂️ 精简冠军</Text>
                <Text>
                  <span className="font-medium">
                    {portrait.repoChampions.slimming.name.split("/").pop()}
                  </span>
                  <span className="text-red-600 ml-2">
                    {portrait.repoChampions.slimming.value.toLocaleString()}
                  </span>
                </Text>
              </Flex>
            )}
          </div>
        </>
      )}
    </Card>
  );
}
