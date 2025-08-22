import { useState, useEffect } from "react";
import {
  searchPlayer,
  searchTeam,
  searchCompetition,
} from "@/services/sports-db";

export type EntityType = "PLAYER" | "COMPETITION" | "TEAM";

interface TrendDetail {
  date: string;
  mentions: number;
}

interface SamplePost {
  text: string;
  sentiment: "positive" | "negative" | "neutral";
  sentiment_score: number;
  date: string;
  username: string;
}

interface SentimentAnalysis {
  positive: number;
  negative: number;
  neutral: number;
}

interface EntityInfo {
  name: string;
  image: string;
  nationality?: string;
  team?: string;
  position?: string;
  hashtags: string[];
}

export interface DetailedDashboardStats {
  total_mentions: number;
  most_popular_hashtag: string;
  most_mentioned_entity: string;
  sentiment_analysis: SentimentAnalysis;
  trend_details: TrendDetail[];
  sample_posts: SamplePost[];
  entity_type: EntityType;
  entity_info?: EntityInfo;
}

const useDetailedStats = (entityType: EntityType) => {
  const [stats, setStats] = useState<DetailedDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `http://localhost:8000/detailed-dashboard-stats/?entity_type=${entityType}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch detailed stats");
        }
        const data = await response.json();

        // Fetch additional entity info from SportsDB
        let entityInfo: EntityInfo | undefined;

        if (data.most_mentioned_entity) {
          if (entityType === "PLAYER") {
            const playerData = await searchPlayer(data.most_mentioned_entity);
            if (playerData) {
              entityInfo = {
                name: playerData.strPlayer,
                image: playerData.strCutout || playerData.strThumb || "",
                nationality: playerData.strNationality,
                team: playerData.strTeam,
                position: playerData.strPosition,
                hashtags: [
                  `#${playerData.strPlayer.replace(/\s+/g, "")}`,
                  `#${playerData.strTeam.replace(/\s+/g, "")}`,
                  `#${playerData.strNationality.replace(/\s+/g, "")}`,
                ],
              };
            }
          } else if (entityType === "TEAM") {
            const teamData = await searchTeam(data.most_mentioned_entity);
            if (teamData) {
              entityInfo = {
                name: teamData.strTeam,
                image: teamData.strTeamBadge,
                nationality: teamData.strCountry,
                hashtags: [
                  `#${teamData.strTeam.replace(/\s+/g, "")}`,
                  `#${teamData.strLeague.replace(/\s+/g, "")}`,
                ],
              };
            }
          } else if (entityType === "COMPETITION") {
            const competitionData = await searchCompetition(
              data.most_mentioned_entity
            );
            if (competitionData) {
              entityInfo = {
                name: competitionData.strLeague,
                image: competitionData.strBadge,
                nationality: competitionData.strCountry,
                hashtags: [
                  `#${competitionData.strLeague.replace(/\s+/g, "")}`,
                  `#${competitionData.strCountry.replace(/\s+/g, "")}`,
                ],
              };
            }
          }
        }

        setStats({ ...data, entity_info: entityInfo });
      } catch (err) {
        setError(err instanceof Error ? err : new Error("Unknown error"));
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [entityType]);

  return { stats, loading, error };
};

export default useDetailedStats;
