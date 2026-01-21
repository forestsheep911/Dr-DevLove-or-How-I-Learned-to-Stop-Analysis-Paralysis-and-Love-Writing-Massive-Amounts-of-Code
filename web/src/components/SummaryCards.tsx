"use client";

interface SummaryCardsProps {
  summary: {
    totalCommits: number;
    totalAdded: number;
    totalDeleted: number;
    netGrowth: number;
    activeDays: number;
    activeRepos: number;
  };
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {/* 总提交数 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">提交数</p>
        <p className="text-2xl font-semibold text-gray-900 mt-1">
          {summary.totalCommits.toLocaleString()}
        </p>
      </div>

      {/* 新增行数 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-green-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">新增</p>
        <p className="text-2xl font-semibold text-green-600 mt-1">
          +{summary.totalAdded.toLocaleString()}
        </p>
      </div>

      {/* 删除行数 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-red-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">删除</p>
        <p className="text-2xl font-semibold text-red-600 mt-1">
          -{summary.totalDeleted.toLocaleString()}
        </p>
      </div>

      {/* 净增长 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">净增长</p>
        <p className={`text-2xl font-semibold mt-1 ${summary.netGrowth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {summary.netGrowth >= 0 ? '+' : ''}{summary.netGrowth.toLocaleString()}
        </p>
      </div>

      {/* 活跃天数 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">活跃天数</p>
        <p className="text-2xl font-semibold text-gray-900 mt-1">
          {summary.activeDays}
          <span className="text-sm font-normal text-gray-500 ml-1">天</span>
        </p>
      </div>

      {/* 活跃仓库 */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
        <p className="text-xs text-gray-500 uppercase tracking-wide">活跃仓库</p>
        <p className="text-2xl font-semibold text-gray-900 mt-1">
          {summary.activeRepos}
          <span className="text-sm font-normal text-gray-500 ml-1">个</span>
        </p>
      </div>
    </div>
  );
}
