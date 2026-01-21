"use client";

import { Card, Title, List, ListItem, Bold, Flex, Text } from "@tremor/react";
import { Highlights } from "@/types/stats";

interface HighlightsCardProps {
  highlights: Highlights;
}

export function HighlightsCard({ highlights }: HighlightsCardProps) {
  const items = [];

  if (highlights.streak && highlights.streak.days > 0) {
    items.push({
      icon: "🔥",
      title: "最长连续提交",
      value: `${highlights.streak.days} 天`,
      detail: `${highlights.streak.start} ~ ${highlights.streak.end}`,
    });
  }

  if (highlights.bestDay) {
    items.push({
      icon: "⭐",
      title: "最活跃日",
      value: highlights.bestDay.date,
      detail: `${highlights.bestDay.commits} 次提交, ${highlights.bestDay.changes.toLocaleString()} 行变更`,
    });
  }

  if (highlights.favoriteWeekday) {
    items.push({
      icon: "📅",
      title: "最爱工作日",
      value: highlights.favoriteWeekday.day,
      detail: `${highlights.favoriteWeekday.commits} 次提交`,
    });
  }

  if (highlights.bestRepo) {
    items.push({
      icon: "🏆",
      title: "最活跃仓库",
      value: highlights.bestRepo.name.split("/").pop() || highlights.bestRepo.name,
      detail: `${highlights.bestRepo.commits} 次提交`,
    });
  }

  if (highlights.longestBreak && highlights.longestBreak.days > 0) {
    items.push({
      icon: "😴",
      title: "最长休息",
      value: `${highlights.longestBreak.days} 天`,
      detail: `${highlights.longestBreak.start} ~ ${highlights.longestBreak.end}`,
    });
  }

  if (items.length === 0) {
    return null;
  }

  return (
    <Card>
      <Title>亮点统计</Title>
      <List className="mt-4">
        {items.map((item, index) => (
          <ListItem key={index}>
            <Flex justifyContent="start" className="space-x-4">
              <span className="text-2xl">{item.icon}</span>
              <div>
                <Text>{item.title}</Text>
                <Bold>{item.value}</Bold>
                <Text className="text-gray-500 text-sm">{item.detail}</Text>
              </div>
            </Flex>
          </ListItem>
        ))}
      </List>
    </Card>
  );
}
