// Define interfaces for the API response data
interface Player {
  idPlayer: string;
  strPlayer: string;
  strNationality: string;
  strTeam: string;
  strPosition: string;
  strCutout: string | null;
  strThumb: string | null;
}

interface Team {
  idTeam: string;
  strTeam: string;
  strCountry: string;
  strTeamBadge: string;
  strLeague: string;
}

interface Competition {
  idLeague: string;
  strLeague: string;
  strCountry: string;
  strBadge: string;
}

// Define API response shapes
interface PlayerResponse {
  player: Player[] | null;
}

interface TeamResponse {
  teams: Team[] | null;
}

interface CompetitionResponse {
  leagues: Competition[] | null;
}

// Base URL for the SportsDB API
const API_BASE_URL = "https://www.thesportsdb.com/api/v1/json/3";

// Function to search for a player
export const searchPlayer = async (
  playerName: string
): Promise<Player | null> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/searchplayers.php?p=${encodeURIComponent(playerName)}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch player data: ${response.statusText}`);
    }
    const data: PlayerResponse = await response.json();
    return data.player && data.player.length > 0 ? data.player[0] : null;
  } catch (error) {
    console.error(`Error fetching player ${playerName}:`, error);
    return null;
  }
};

// Function to search for a team
export const searchTeam = async (teamName: string): Promise<Team | null> => {
  teamName = teamName === "النصر" ? "Al Nasr" : teamName;
  try {
    const response = await fetch(
      `${API_BASE_URL}/searchteams.php?t=${encodeURIComponent(teamName)}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch team data: ${response.statusText}`);
    }
    const data: TeamResponse = await response.json();
    return data.teams && data.teams.length > 0 ? data.teams[0] : null;
  } catch (error) {
    console.error(`Error fetching team ${teamName}:`, error);
    return null;
  }
};

// Function to search for a competition
export const searchCompetition = async (
  competitionName: string
): Promise<Competition | null> => {
  try {
    competitionName =
      competitionName === "نهائي كاس ملك اسبانيا"
        ? "Spanish King's Cup Final"
        : competitionName;

    const response = await fetch(
      `${API_BASE_URL}/searchleagues.php?l=${encodeURIComponent(
        competitionName
      )}`
    );
    if (!response.ok) {
      throw new Error(
        `Failed to fetch competition data: ${response.statusText}`
      );
    }
    const data: CompetitionResponse = await response.json();
    return data.leagues && data.leagues.length > 0 ? data.leagues[0] : null;
  } catch (error) {
    console.error(`Error fetching competition ${competitionName}:`, error);
    return null;
  }
};
