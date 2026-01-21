/**
 * GitHub 统计数据类型定义
 */

export interface StatsData {
  meta: {
    user: string;
    dateRange: {
      since: string;
      until: string;
    };
    generatedAt: string;
    mode: 'personal' | 'org-summary';
    org?: string;
  };
  summary: {
    totalCommits: number;
    totalAdded: number;
    totalDeleted: number;
    netGrowth: number;
    activeDays: number;
    activeRepos: number;
  };
  repos: RepoStats[];
  timeline: TimelineEntry[];
  highlights?: Highlights;
  portrait?: Portrait;
  arena?: ArenaEntry[];
}

export interface RepoStats {
  name: string;
  commits: number;
  added: number;
  deleted: number;
}

export interface TimelineEntry {
  date: string;
  commits: number;
  added: number;
  deleted: number;
}

export interface Highlights {
  streak?: {
    days: number;
    start: string;
    end: string;
  };
  bestDay?: {
    date: string;
    commits: number;
    changes: number;
  };
  favoriteWeekday?: {
    day: string;
    dayIndex: number;
    commits: number;
    changes: number;
  };
  bestRepo?: {
    name: string;
    commits: number;
  };
  longestBreak?: {
    days: number;
    start: string;
    end: string;
  };
}

export interface Portrait {
  weekdayStats: Record<number, number>;
  hourStats: Record<number, number>;
  avgLinesPerCommit: number;
  repoChampions?: {
    growth?: { name: string; value: number };
    refactor?: { name: string; value: number };
    slimming?: { name: string; value: number };
  };
}

export interface ArenaEntry {
  rank: number;
  user: string;
  commits: number;
  added: number;
  deleted: number;
  netGrowth: number;
}

// 工作日名称
export const WEEKDAY_NAMES = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
export const WEEKDAY_NAMES_EN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
