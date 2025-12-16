/**
 * API client for LinkedScraper backend (SERP Aggregator)
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout for SERP requests
});

// Types matching backend SERP Aggregator
export interface SearchRequest {
  role: string;
  location: string;
  country: string;
  language: string;
  max_pages: number;
}

export interface LinkedInProfile {
  profile_url: string;
  title: string;
  description: string | null;
  rank: number;
  best_position: number;
  avg_position: number;
  frequency: number;
  pages_seen: number[];
}

export interface SearchResponse {
  query: string;
  total_results: number;
  profiles: LinkedInProfile[];
  metadata: {
    country: string;
    language: string;
    pages_fetched: number;
    search_engine: string;
    has_errors: boolean;
  };
}

// Backend LinkedScraper response structure (already parsed!)
interface BackendProfile {
  name: string;
  headline: string | null;
  location: string | null;
  company: string | null;
  education: string | null;
  connections: number | null;
  profile_url: string;
  rank: number;
  best_position: number;
  frequency: number;
  pages_seen: number[];
}

interface BackendSearchResponse {
  success: boolean;
  query: string;
  total_results: number;
  profiles: BackendProfile[];
  metadata: {
    country: string;
    language: string;
    pages_requested: number;
    pages_scraped: number;
    time_taken_seconds: number;
  };
}

// API Functions
export const searchLinkedIn = async (params: SearchRequest): Promise<SearchResponse> => {
  // Send request to LinkedScraper custom backend
  const backendRequest = {
    role: params.role,
    location: params.location,
    country: params.country,
    language: params.language,
    max_pages: params.max_pages,
  };

  const response = await apiClient.post<BackendSearchResponse>('/search', backendRequest);
  const backendResult = response.data;

  // Transform backend profiles to frontend format
  const profiles: LinkedInProfile[] = backendResult.profiles.map(profile => ({
    profile_url: profile.profile_url,
    title: `${profile.name}${profile.headline ? ' - ' + profile.headline : ''}`,
    description: [profile.company, profile.location, profile.education]
      .filter(Boolean)
      .join(' • '),
    rank: profile.rank,
    best_position: profile.best_position,
    avg_position: profile.best_position, // Backend doesn't provide avg, use best_position
    frequency: profile.frequency,
    pages_seen: profile.pages_seen,
  }));

  return {
    query: backendResult.query,
    total_results: backendResult.total_results,
    profiles,
    metadata: {
      country: backendResult.metadata.country,
      language: backendResult.metadata.language,
      pages_fetched: backendResult.metadata.pages_scraped,
      search_engine: 'google',
      has_errors: !backendResult.success,
    },
  };
};

export const testAPI = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};
