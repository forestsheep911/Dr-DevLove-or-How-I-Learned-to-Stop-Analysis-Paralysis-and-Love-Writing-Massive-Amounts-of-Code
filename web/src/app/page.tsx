"use client";

import { useEffect, useState } from "react";
import { StatsData } from "@/types/stats";
import { SummaryCards } from "@/components/SummaryCards";
import { CommitChart } from "@/components/CommitChart";
import { RepoChart } from "@/components/RepoChart";
import { StatsTable } from "@/components/StatsTable";
import { HighlightsCard } from "@/components/HighlightsCard";
import { PortraitCard } from "@/components/PortraitCard";
import { ArenaCard } from "@/components/ArenaCard";

export default function Home() {
  const [data, setData] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data.json")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load data");
        return res.json();
      })
      .then((data: StatsData) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">加载统计数据中...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center text-red-500">
          <p className="text-xl mb-2">加载失败</p>
          <p className="text-gray-600">{error || "无法加载数据"}</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dr. DevLove 统计报告
        </h1>
        <p className="text-gray-600">
          {data.meta.user && <span className="font-medium">{data.meta.user}</span>}
          {data.meta.org && (
            <span className="font-medium"> @ {data.meta.org}</span>
          )}
          <span className="mx-2">|</span>
          <span>
            {data.meta.dateRange.since} ~ {data.meta.dateRange.until}
          </span>
        </p>
      </header>

      {/* Summary Cards */}
      <section className="mb-8">
        <SummaryCards summary={data.summary} />
      </section>

      {/* Charts Row */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <CommitChart timeline={data.timeline} />
        <RepoChart repos={data.repos} />
      </section>

      {/* Stats Table */}
      <section className="mb-8">
        <StatsTable repos={data.repos} />
      </section>

      {/* Highlights & Portrait */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {data.highlights && <HighlightsCard highlights={data.highlights} />}
        {data.portrait && <PortraitCard portrait={data.portrait} />}
      </section>

      {/* Arena (if org-summary mode) */}
      {data.arena && data.arena.length > 0 && (
        <section className="mb-8">
          <ArenaCard arena={data.arena} />
        </section>
      )}

      {/* Footer */}
      <footer className="text-center text-gray-500 text-sm pt-8 border-t">
        <p>
          生成时间: {new Date(data.meta.generatedAt).toLocaleString("zh-CN")}
        </p>
        <p className="mt-1">
          Powered by{" "}
          <a
            href="https://github.com/user/gh-stats"
            className="text-blue-500 hover:underline"
          >
            Dr. DevLove (gh-stats)
          </a>
        </p>
      </footer>
    </main>
  );
}
