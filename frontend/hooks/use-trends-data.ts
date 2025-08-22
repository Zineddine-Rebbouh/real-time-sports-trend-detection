import { useState, useEffect } from "react";

export type EntityType = "PLAYER" | "TEAM" | "COMPETITION";
export type SportType = "كرة_القدم" | "كرة_السلة" | "تنس" | "ملاكمة";

interface TrendDetail {
  date: string;
  mentions: number;
}

interface SampleComment {
  text: string;
  sentiment: "positive" | "negative" | "neutral";
  sentiment_score: number;
  date: string;
  sport_type: string;
}

interface SentimentAnalysis {
  positive: number;
  neutral: number;
  negative: number;
  average_score: number;
}

interface EntityInfo {
  name: string;
  image: string;
  nationality?: string;
  team?: string;
  position?: string;
  hashtags: string[];
}

export interface TrendData {
  entity_text: string;
  count: number;
  trend_details: TrendDetail[];
  sample_comments: SampleComment[];
  sentiment: SentimentAnalysis;
  entity_info?: EntityInfo;
}

function useTrendsData(sportType: SportType, entityType: EntityType) {
  const [data, setData] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchTrendData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/get_trend_by_sports_type?sport_type=${sportType}&entity_type=${entityType}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch trend data");
        }
        const responseData = await response.json();
        setData(responseData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error("Unknown error"));
      } finally {
        setLoading(false);
      }
    };

    fetchTrendData();
  }, [sportType, entityType]);

  return { data, loading, error };
}

export { useTrendsData };
