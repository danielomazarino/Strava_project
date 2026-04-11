import { env } from '$env/dynamic/private';
import { dev } from '$app/environment';
import type { RequestHandler } from './$types';

const hopByHopHeaders = new Set([
	'connection',
	'content-length',
	'keep-alive',
	'proxy-authenticate',
	'proxy-authorization',
	'te',
	'trailer',
	'transfer-encoding',
	'upgrade'
]);

function getBackendBaseUrl() {
	const backendBaseUrl = env.BACKEND_API_BASE_URL?.trim() ?? '';
	if (backendBaseUrl) {
		return backendBaseUrl.replace(/\/$/, '');
	}

	return dev ? 'http://127.0.0.1:8000' : 'https://web-production-5434a.up.railway.app';
}

function copyHeaders(headers: Headers) {
	const forwardedHeaders = new Headers();
	for (const [key, value] of headers.entries()) {
		if (!hopByHopHeaders.has(key.toLowerCase())) {
			forwardedHeaders.set(key, value);
		}
	}
	return forwardedHeaders;
}

async function proxy({ request, url, params }: Parameters<RequestHandler>[0]) {
	const backendBaseUrl = getBackendBaseUrl();
	if (!backendBaseUrl) {
		return new Response('Backend API base URL is not configured', { status: 500 });
	}

	const targetUrl = new URL(params.path ? `/${params.path}` : '/', backendBaseUrl);
	targetUrl.search = url.search;

	const headers = new Headers(request.headers);
	headers.delete('host');
	headers.delete('content-length');

	const body = request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.arrayBuffer();
	const backendResponse = await fetch(targetUrl, {
		method: request.method,
		headers,
		body,
		redirect: 'manual'
	});

	return new Response(backendResponse.body, {
		status: backendResponse.status,
		headers: copyHeaders(backendResponse.headers)
	});
}

export const GET: RequestHandler = proxy;
export const HEAD: RequestHandler = proxy;
export const POST: RequestHandler = proxy;
export const PUT: RequestHandler = proxy;
export const PATCH: RequestHandler = proxy;
export const DELETE: RequestHandler = proxy;
export const OPTIONS: RequestHandler = proxy;