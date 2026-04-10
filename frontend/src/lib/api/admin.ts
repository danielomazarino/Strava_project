import { apiRequest } from './client';
import type { ApiStatusResponse, TokenHealth } from './models';

export type AdminActivitySummary = {
	id: string;
	user_id: string;
	user_strava_athlete_id: number;
	strava_activity_id: number;
	name: string | null;
	type: string | null;
	start_date: string;
	distance: number | null;
	moving_time: number | null;
	elapsed_time: number | null;
	elevation_gain: number | null;
	description: string | null;
	polyline: string | null;
	timezone: string | null;
	location_country: string | null;
	has_raw_payload: boolean;
	token_health: TokenHealth;
	raw_payload: Record<string, unknown> | null;
	created_at: string | null;
	updated_at: string | null;
};

export type AdminUserSummary = {
	id: string;
	strava_athlete_id: number;
	token_expires_at: string;
	token_health: TokenHealth;
	activity_count: number;
	latest_activity_start_date: string | null;
	latest_activity_name: string | null;
	latest_activity_country: string | null;
};

export type AdminTotals = {
	users: number;
	activities: number;
	active_tokens: number;
	expiring_tokens: number;
	expired_tokens: number;
};

export type AdminOverviewResponse = ApiStatusResponse & {
	generated_at: string;
	totals: AdminTotals;
	users: AdminUserSummary[];
	recent_activities: AdminActivitySummary[];
	records: AdminActivitySummary[];
};

export async function getAdminOverview(): Promise<AdminOverviewResponse> {
	return apiRequest<AdminOverviewResponse>('/admin/overview');
}