import { useState, useEffect } from "react";

interface WordCloudItem {
  word: string;
  count: number;
}

interface SentimentAnalysis {
  positive: number;
  negative: number;
  neutral: number;
}

interface TrendDetails {
  date: string;
  mentions: number;
}

interface EntityMention {
  entity_text: string;
  count: number;
  trend_details: TrendDetails[];
}

interface DashboardStats {
  total_posts: number;
  most_popular_hashtag: string;
  most_mentioned_player: EntityMention;
  most_mentioned_team: EntityMention;
  most_mentioned_competition: EntityMention;
  sentiment_analysis: SentimentAnalysis;
  word_cloud: WordCloudItem[];
}

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch("http://localhost:8000/dashboard-stats/");
        if (!response.ok) {
          throw new Error("Failed to fetch dashboard stats");
        }
        const data = await response.json();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err : new Error("Unknown error"));
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
}
