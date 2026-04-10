import { apiRequest, resolveApiUrl } from './client';

export type OAuthCallbackResponse = {
	status: 'connected';
	user_id: string;
	strava_athlete_id: number;
};

export function getStravaLoginUrl(): string {
	return resolveApiUrl('/auth/login');
}

export async function completeOAuthCallback(code: string, state: string): Promise<OAuthCallbackResponse> {
	const query = new URLSearchParams({ code, state });
	return apiRequest<OAuthCallbackResponse>(`/auth/callback?${query.toString()}`);
}