"use client";

import { Card, Title, BarList, Flex, Text } from "@tremor/react";
import { RepoStats } from "@/types/stats";

interface RepoChartProps {
  repos: RepoStats[];
}

export function RepoChart({ repos }: RepoChartProps) {
  // 按提交数排序，取前 10
  const topRepos = [...repos]
    .sort((a, b) => b.commits - a.commits)
    .slice(0, 10);

  const chartData = topRepos.map((repo) => ({
    name: repo.name.split("/").pop() || repo.name,
    value: repo.commits,
    href: `https://github.com/${repo.name}`,
  }));

  const totalCommits = repos.reduce((sum, r) => sum + r.commits, 0);

  return (
    <Card>
      <Title>仓库贡献 (Top 10)</Title>
      <Flex className="mt-4">
        <Text>仓库</Text>
        <Text>提交数</Text>
      </Flex>
      <BarList
        data={chartData}
        className="mt-2"
        valueFormatter={(value: number) => `${value} (${((value / totalCommits) * 100).toFixed(1)}%)`}
        showAnimation={true}
      />
    </Card>
  );
}
