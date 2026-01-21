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
import { ArenaEntry } from "@/types/stats";

interface ArenaCardProps {
  arena: ArenaEntry[];
}

export function ArenaCard({ arena }: ArenaCardProps) {
  // 获取排名徽章
  const getRankBadge = (rank: number) => {
    switch (rank) {
      case 1:
        return <span className="text-2xl">🥇</span>;
      case 2:
        return <span className="text-2xl">🥈</span>;
      case 3:
        return <span className="text-2xl">🥉</span>;
      default:
        return <Badge color="gray">{rank}</Badge>;
    }
  };

  return (
    <Card>
      <Title>竞技场排名</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>排名</TableHeaderCell>
            <TableHeaderCell>贡献者</TableHeaderCell>
            <TableHeaderCell className="text-right">提交数</TableHeaderCell>
            <TableHeaderCell className="text-right">新增行</TableHeaderCell>
            <TableHeaderCell className="text-right">删除行</TableHeaderCell>
            <TableHeaderCell className="text-right">净增长</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {arena.map((entry) => (
            <TableRow key={entry.rank}>
              <TableCell>{getRankBadge(entry.rank)}</TableCell>
              <TableCell>
                <a
                  href={`https://github.com/${entry.user}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline font-medium"
                >
                  {entry.user}
                </a>
              </TableCell>
              <TableCell className="text-right font-medium">
                {entry.commits}
              </TableCell>
              <TableCell className="text-right text-green-600">
                +{entry.added.toLocaleString()}
              </TableCell>
              <TableCell className="text-right text-red-600">
                -{entry.deleted.toLocaleString()}
              </TableCell>
              <TableCell className="text-right">
                <Badge color={entry.netGrowth >= 0 ? "green" : "red"}>
                  {entry.netGrowth >= 0 ? "+" : ""}
                  {entry.netGrowth.toLocaleString()}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
