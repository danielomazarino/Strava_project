import { apiRequest, buildQueryString } from './client';
import type { ApiStatusResponse, PatternInsight, RegionComparisonInsight, SummaryInsight } from './models';

export type SummaryInsightResponse = ApiStatusResponse & {
	analysis: SummaryInsight;
};

export type PatternInsightResponse = ApiStatusResponse & {
	analysis: PatternInsight;
};

export type RegionComparisonResponse = ApiStatusResponse & {
	analysis: RegionComparisonInsight;
};

export async function getSummaryInsight(
	stravaAthleteId: number,
	startDate: Date | string,
	endDate: Date | string
): Promise<SummaryInsightResponse> {
	const query = buildQueryString({
		strava_athlete_id: stravaAthleteId,
		start_date: typeof startDate === 'string' ? startDate : new Date(startDate).toISOString(),
		end_date: typeof endDate === 'string' ? endDate : new Date(endDate).toISOString()
	});

	return apiRequest<SummaryInsightResponse>(`/insights/summary?${query}`);
}

export async function getPatternInsight(
	stravaAthleteId: number,
	startDate: Date | string,
	endDate: Date | string
): Promise<PatternInsightResponse> {
	const query = buildQueryString({
		strava_athlete_id: stravaAthleteId,
		start_date: typeof startDate === 'string' ? startDate : new Date(startDate).toISOString(),
		end_date: typeof endDate === 'string' ? endDate : new Date(endDate).toISOString()
	});

	return apiRequest<PatternInsightResponse>(`/insights/patterns?${query}`);
}

export async function compareRegions(
	stravaAthleteId: number,
	regionA: string,
	regionB: string,
	startDate?: Date | string,
	endDate?: Date | string
): Promise<RegionComparisonResponse> {
	const query = buildQueryString({
		strava_athlete_id: stravaAthleteId,
		region_a: regionA,
		region_b: regionB,
		start_date: startDate == null ? undefined : typeof startDate === 'string' ? startDate : new Date(startDate).toISOString(),
		end_date: endDate == null ? undefined : typeof endDate === 'string' ? endDate : new Date(endDate).toISOString()
	});

	return apiRequest<RegionComparisonResponse>(`/insights/regions/comparison?${query}`);
}