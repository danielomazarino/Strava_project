import { apiRequest, buildQueryString } from './client';
import type { HeatmapResponse } from './models';

export type HeatmapQuery = {
	stravaAthleteId: number;
	startDate?: Date | string;
	endDate?: Date | string;
	activityType?: string;
	country?: string;
};

export async function getHeatmapTile(z: number, x: number, y: number, query: HeatmapQuery): Promise<HeatmapResponse> {
	const qs = buildQueryString({
		strava_athlete_id: query.stravaAthleteId,
		start_date: query.startDate == null ? undefined : typeof query.startDate === 'string' ? query.startDate : query.startDate.toISOString(),
		end_date: query.endDate == null ? undefined : typeof query.endDate === 'string' ? query.endDate : query.endDate.toISOString(),
		activity_type: query.activityType,
		country: query.country
	});

	return apiRequest<HeatmapResponse>(`/heatmaps/tiles/${z}/${x}/${y}?${qs}`);
}