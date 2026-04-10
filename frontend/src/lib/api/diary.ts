import { apiRequest, buildQueryString } from './client';
import type { ApiStatusResponse, DiaryEntry } from './models';

export type DiaryResponse = ApiStatusResponse & {
	entries: DiaryEntry[];
};

export async function listDiaryEntries(stravaAthleteId: number): Promise<DiaryResponse> {
	const query = buildQueryString({ strava_athlete_id: stravaAthleteId });
	return apiRequest<DiaryResponse>(`/diary?${query}`);
}