import { apiRequest, buildQueryString } from './client';
import type { ActivityDetail, ActivityImportResult } from './models';

export type ImportActivitiesParams = {
	after?: number;
	before?: number;
};

export async function importActivities(
	stravaAthleteId: number,
	params: ImportActivitiesParams = {}
): Promise<ActivityImportResult> {
	const query = buildQueryString({
		strava_athlete_id: stravaAthleteId,
		after: params.after,
		before: params.before
	});

	return apiRequest<ActivityImportResult>(`/activities/import?${query}`);
}

export type ActivityResponse = {
	status: 'ok';
	activity: ActivityDetail;
};

export async function getActivityDetails(
	stravaAthleteId: number,
	stravaActivityId: number
): Promise<ActivityResponse> {
	const query = buildQueryString({ strava_athlete_id: stravaAthleteId });
	return apiRequest<ActivityResponse>(`/activities/${stravaActivityId}?${query}`);
}