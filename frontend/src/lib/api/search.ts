import { apiRequest, buildQueryString } from './client';
import type { ApiStatusResponse, SearchResult } from './models';

export type SearchResponse = ApiStatusResponse & {
	results: SearchResult[];
};

export async function keywordSearch(stravaAthleteId: number, queryText: string): Promise<SearchResponse> {
	const query = buildQueryString({ strava_athlete_id: stravaAthleteId, q: queryText });
	return apiRequest<SearchResponse>(`/search/keyword?${query}`);
}

export async function semanticSearch(stravaAthleteId: number, queryText: string): Promise<SearchResponse> {
	const query = buildQueryString({ strava_athlete_id: stravaAthleteId, q: queryText });
	return apiRequest<SearchResponse>(`/search/semantic?${query}`);
}