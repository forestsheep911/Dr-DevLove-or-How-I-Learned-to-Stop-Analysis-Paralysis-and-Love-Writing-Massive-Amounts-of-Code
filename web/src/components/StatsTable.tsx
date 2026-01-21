"use client";

import {
  Card,
  Title,
  Table,
  TableHead,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  Badge,
} from "@tremor/react";
import { RepoStats } from "@/types/stats";

interface StatsTableProps {
  repos: RepoStats[];
}

export function StatsTable({ repos }: StatsTableProps) {
  // 按提交数排序
  const sortedRepos = [...repos].sort((a, b) => b.commits - a.commits);

  return (
    <Card>
      <Title>仓库统计详情</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>仓库</TableHeaderCell>
            <TableHeaderCell className="text-right">提交数</TableHeaderCell>
            <TableHeaderCell className="text-right">新增行</TableHeaderCell>
            <TableHeaderCell className="text-right">删除行</TableHeaderCell>
            <TableHeaderCell className="text-right">净变更</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {sortedRepos.map((repo) => {
            const netChange = repo.added - repo.deleted;
            return (
              <TableRow key={repo.name}>
                <TableCell>
                  <a
                    href={`https://github.com/${repo.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {repo.name}
                  </a>
                </TableCell>
                <TableCell className="text-right">{repo.commits}</TableCell>
                <TableCell className="text-right text-green-600">
                  +{repo.added.toLocaleString()}
                </TableCell>
                <TableCell className="text-right text-red-600">
                  -{repo.deleted.toLocaleString()}
                </TableCell>
                <TableCell className="text-right">
                  <Badge color={netChange >= 0 ? "green" : "red"}>
                    {netChange >= 0 ? "+" : ""}
                    {netChange.toLocaleString()}
                  </Badge>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
