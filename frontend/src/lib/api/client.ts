import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';

import { getDemoApiResponse } from './demo-data';

function normalizeBaseUrl(baseUrl: string | undefined): string {
	if (!baseUrl) {
		return '';
	}
	return baseUrl.replace(/\/$/, '');
}

export function getPublicApiBaseUrl(): string {
	const configuredBaseUrl = normalizeBaseUrl(env.PUBLIC_API_BASE_URL);
	if (configuredBaseUrl) {
		if (!dev && /^https?:\/\//.test(configuredBaseUrl)) {
			return '/api';
		}

		return configuredBaseUrl;
	}

	return dev ? '' : '/api';
}

export function resolveApiUrl(path: string): string {
	if (/^https?:\/\//.test(path)) {
		return path;
	}

	const normalizedPath = path.startsWith('/') ? path : `/${path}`;
	const baseUrl = getPublicApiBaseUrl();
	return baseUrl ? `${baseUrl}${normalizedPath}` : normalizedPath;
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
	const baseUrl = getPublicApiBaseUrl();
	if (!baseUrl) {
		if (!dev) {
			throw new Error('Frontend API base URL is not configured');
		}

		return getDemoApiResponse(path) as T;
	}

	const response = await fetch(resolveApiUrl(path), {
		...init,
		headers: {
			'Content-Type': 'application/json',
			...(init.headers ?? {})
		}
	});

	if (!response.ok) {
		const details = await response.text();
		throw new Error(details || `Request failed with status ${response.status}`);
	}

	if (response.status === 204) {
		return undefined as T;
	}

	return (await response.json()) as T;
}

type QueryValue = string | number | boolean | Date | null | undefined;

export function buildQueryString(params: Record<string, QueryValue>): string {
	const query = new URLSearchParams();

	for (const [key, value] of Object.entries(params)) {
		if (value === null || value === undefined) {
			continue;
		}

		query.set(key, value instanceof Date ? value.toISOString() : String(value));
	}

	return query.toString();
}