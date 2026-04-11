import { redirect } from '@sveltejs/kit';
import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';

import { getPublicApiBaseUrl, resolveApiUrl } from '$lib/api/client';

export const load = ({ url }) => {
	const apiBaseUrl = getPublicApiBaseUrl();
	const loginUrl = resolveApiUrl('/auth/login');
	const mockAuthEnabled = dev && env.PUBLIC_ENABLE_DEV_MOCK_AUTH === 'true';
	const demoSessionAvailable = dev && !apiBaseUrl;

	if (mockAuthEnabled && apiBaseUrl) {
		const callbackUrl = new URL('/auth/callback', url.origin).toString();
		throw redirect(302, resolveApiUrl(`/auth/mock-login?return_to=${encodeURIComponent(callbackUrl)}`));
	}

	if (apiBaseUrl && new URL(loginUrl, url.origin).origin !== url.origin) {
		throw redirect(302, loginUrl);
	}

	return {
		apiBaseConfigured: Boolean(apiBaseUrl),
		mockAuthEnabled,
		demoSessionAvailable
	};
};