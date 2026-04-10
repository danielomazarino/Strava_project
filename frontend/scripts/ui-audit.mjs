import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';

const BASE_URL = process.env.AUDIT_BASE_URL ?? 'http://127.0.0.1:5173';
const API_BASE_URL = process.env.AUDIT_API_BASE_URL ?? 'http://127.0.0.1:8000';
const AUDIT_TIMEOUT_MS = Number(process.env.AUDIT_TIMEOUT_MS ?? 120000);
const HEALTHCHECK_TIMEOUT_MS = Number(process.env.AUDIT_HEALTHCHECK_TIMEOUT_MS ?? 8000);
const BROWSER_LAUNCH_TIMEOUT_MS = Number(process.env.AUDIT_BROWSER_LAUNCH_TIMEOUT_MS ?? 20000);
const ROUTE_NAVIGATION_TIMEOUT_MS = Number(process.env.AUDIT_ROUTE_NAVIGATION_TIMEOUT_MS ?? 15000);
const ROUTE_SETTLE_TIMEOUT_MS = Number(process.env.AUDIT_ROUTE_SETTLE_TIMEOUT_MS ?? 2500);
const SCREENSHOT_DIR = process.env.AUDIT_SCREENSHOT_DIR ?? 'audit-screenshots';
const CAPTURE_SCREENSHOTS = (process.env.AUDIT_CAPTURE_SCREENSHOTS ?? 'true').toLowerCase() !== 'false';
const STORAGE_KEY = 'strava-training-diary-session';
const DEMO_SESSION = {
	status: 'connected',
	userId: 'demo-user',
	stravaAthleteId: 14706324,
	connectedAt: '2026-04-08T20:00:00.000Z'
};

const ROUTES = [
	'/',
	'/dashboard',
	'/diary',
	'/diary/9100008',
	'/charts',
	'/insights',
	'/heatmap',
	'/routes',
	'/search',
	'/semantic-search',
	'/compare',
	'/settings',
	'/about'
];

const EMPTY_STATE_PATTERNS = [
	/Failed to fetch/i,
	/No activities loaded yet/i,
	/No matching activities/i,
	/No entries yet/i,
	/No active session yet/i,
	/No saved session yet/i,
	/No data/i,
	/Unable to load/i,
	/Anonymous/i
];

const HIGH_LINK_COUNT = 10;
const HIGH_BUTTON_COUNT = 5;
const HIGH_SURFACE_COUNT = 6;
const HIGH_TILE_COUNT = 10;

function labelForUrl(url) {
	return new URL(url).pathname.replace(/\/$/, '') || '/';
}

function unique(values) {
	return [...new Set(values.filter(Boolean))];
}

function routeScreenshotName(route) {
	const slug = route.replace(/^\//, '').replace(/\//g, '-').replace(/[^a-zA-Z0-9-]+/g, '-');
	return `${slug || 'home'}.png`;
}

async function waitForApiRequestsToSettle(page, pendingRequests, timeoutMs) {
	const start = Date.now();
	let settledAt = 0;

	while (Date.now() - start < timeoutMs) {
		if (pendingRequests.size === 0) {
			if (settledAt === 0) {
				settledAt = Date.now();
			} else if (Date.now() - settledAt >= 400) {
				return;
			}
		} else {
			settledAt = 0;
		}

		await page.waitForTimeout(100);
	}
}

async function runAuthSmokeCheck(browser) {
	const context = await browser.newContext({ viewport: { width: 1440, height: 1600 } });
	context.setDefaultTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);
	context.setDefaultNavigationTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);

	const page = await context.newPage();
	try {
		await page.goto(`${BASE_URL}/auth/login`, { waitUntil: 'domcontentloaded', timeout: ROUTE_NAVIGATION_TIMEOUT_MS });
		await page.waitForLoadState('networkidle', { timeout: ROUTE_SETTLE_TIMEOUT_MS }).catch(() => {});

		const currentUrl = new URL(page.url());
		if (currentUrl.pathname === '/auth/callback') {
			await page.waitForURL('**/diary', { timeout: ROUTE_NAVIGATION_TIMEOUT_MS });
			await page.waitForLoadState('networkidle', { timeout: ROUTE_SETTLE_TIMEOUT_MS }).catch(() => {});
			return;
		}

		if (currentUrl.pathname === '/diary' || currentUrl.pathname === '/dashboard') {
			return;
		}

		if (currentUrl.pathname !== '/auth/login') {
			throw new Error(`Auth smoke test expected to stay on /auth/login or redirect to /auth/callback, got ${currentUrl.pathname}`);
		}

		const startDemoSession = page.getByRole('button', { name: 'Start demo session' });
		if (await startDemoSession.count()) {
			await startDemoSession.click();
			await page.waitForURL('**/dashboard', { timeout: ROUTE_NAVIGATION_TIMEOUT_MS });
			await page.waitForLoadState('networkidle', { timeout: ROUTE_SETTLE_TIMEOUT_MS }).catch(() => {});
			return;
		}

		const skipButton = page.getByRole('button', { name: 'Skip for now' });
		if (await skipButton.count()) {
			await skipButton.click();
			await page.waitForURL('**/dashboard', { timeout: ROUTE_NAVIGATION_TIMEOUT_MS });
			await page.waitForLoadState('networkidle', { timeout: ROUTE_SETTLE_TIMEOUT_MS }).catch(() => {});
			return;
		}

		throw new Error('Auth smoke test could not find a login action or redirect target');
	} finally {
		await page.close();
		await context.close();
	}
}

async function preflightCheck(label, url) {
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), HEALTHCHECK_TIMEOUT_MS);

	try {
		const response = await fetch(url, { signal: controller.signal });
		if (!response.ok) {
			throw new Error(`${label} returned HTTP ${response.status}`);
		}
	} catch (error) {
		const message = error instanceof Error ? error.message : String(error);
		throw new Error(`${label} preflight failed for ${url}: ${message}`);
	} finally {
		clearTimeout(timeoutId);
	}
}

function summarizeWarnings(stats) {
	const warnings = [];

	if (stats.routeError) {
		warnings.push(`route error: ${stats.routeError}`);
	}

	if (stats.primaryNavLinkCount >= HIGH_LINK_COUNT) {
		warnings.push(`sidebar link-heavy (${stats.primaryNavLinkCount} links)`);
	}

	if (stats.linkCount >= HIGH_LINK_COUNT) {
		warnings.push(`overall link-heavy (${stats.linkCount} visible links)`);
	}

	if (stats.buttonCount >= HIGH_BUTTON_COUNT) {
		warnings.push(`button-heavy (${stats.buttonCount} visible buttons)`);
	}

	if (stats.surfacePanelCount >= HIGH_SURFACE_COUNT || stats.sectionBlockCount >= HIGH_TILE_COUNT) {
		warnings.push(`tile-heavy (${stats.surfacePanelCount} panels, ${stats.sectionBlockCount} section blocks)`);
	}

	if (stats.emptyStates.length > 0) {
		warnings.push(`empty/failure states: ${stats.emptyStates.join(' | ')}`);
	}

	if (stats.failedRequests.length > 0) {
		warnings.push(`request failures: ${stats.failedRequests.map((item) => `${item.method} ${item.url} (${item.error})`).join(' | ')}`);
	}

	return warnings;
}

async function collectRouteStats(page) {
	return page.evaluate(({ emptyPatterns }) => {
		const unique = (values) => [...new Set(values.filter(Boolean))];

		const isVisible = (node) => {
			if (!(node instanceof HTMLElement)) {
				return false;
			}

			const style = window.getComputedStyle(node);
			const rect = node.getBoundingClientRect();
			return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
		};

		const text = (node) => node.textContent?.replace(/\s+/g, ' ').trim() ?? '';

		const visibleNodes = (selector) => [...document.querySelectorAll(selector)].filter(isVisible);
		const visibleTexts = (selector) => visibleNodes(selector).map(text).filter(Boolean);

		const primaryNav = document.querySelector('nav[aria-label="Primary navigation"]');
		const primaryNavLinks = primaryNav
			? [...primaryNav.querySelectorAll('a')].filter(isVisible).map(text).filter(Boolean)
			: [];

		const allLinks = visibleTexts('a');
		const allButtons = visibleTexts('button');
		const surfacePanels = visibleNodes('.surface-panel');
		const sectionBlocks = visibleNodes('.section-block');
		const infoBubbles = visibleNodes('.info-bubble');
		const tables = visibleNodes('table');
		const tableRows = visibleNodes('tbody tr');
		const headings = visibleTexts('h1, h2, h3, h4');
		const lines = document.body.innerText.split('\n').map((line) => line.trim()).filter(Boolean);
		const compiledPatterns = emptyPatterns.map(({ source, flags }) => new RegExp(source, flags));
		const emptyStates = unique(lines.filter((line) => compiledPatterns.some((pattern) => pattern.test(line))));
		const keyMetrics = unique(
			lines.filter((line) => /^\d+[\d,.\s]*(km|m|h|activities|entries|tokens|users)?$/i.test(line) || /km|m\b|activities|entries|tokens|users/i.test(line))
		).slice(0, 12);

		return {
			linkCount: allLinks.length,
			buttonCount: allButtons.length,
			primaryNavLinkCount: primaryNavLinks.length,
			primaryNavLinks,
			topLinks: allLinks.slice(0, 12),
			topButtons: allButtons.slice(0, 12),
			surfacePanelCount: surfacePanels.length,
			sectionBlockCount: sectionBlocks.length,
			infoBubbleCount: infoBubbles.length,
			tableCount: tables.length,
			tableRowCount: tableRows.length,
			headings: headings.slice(0, 12),
			emptyStates,
			keyMetrics,
			pageTitle: document.title,
			currentHeading: headings[0] ?? ''
		};
	}, { emptyPatterns: EMPTY_STATE_PATTERNS.map((pattern) => ({ source: pattern.source, flags: pattern.flags })) });
}

async function main() {
	const stopAt = setTimeout(() => {
		console.error(`UI audit exceeded ${AUDIT_TIMEOUT_MS}ms`);
		process.exit(1);
	}, AUDIT_TIMEOUT_MS);
	let browser;
	try {
		await preflightCheck('frontend', BASE_URL);
		await preflightCheck('backend', `${API_BASE_URL}/health`);
		if (CAPTURE_SCREENSHOTS) {
			await mkdir(SCREENSHOT_DIR, { recursive: true });
		}

		try {
			browser = await chromium.launch({ headless: true, timeout: BROWSER_LAUNCH_TIMEOUT_MS });
		} catch (error) {
			const message = error instanceof Error ? error.message : String(error);
			throw new Error(
				`Unable to launch Chromium for the UI audit. If Playwright browsers are missing, run 'npx playwright install chromium'. Original error: ${message}`
			);
		}

		const context = await browser.newContext({ viewport: { width: 1440, height: 1600 } });
		context.setDefaultTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);
		context.setDefaultNavigationTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);

		await context.addInitScript(
			({ storageKey, sessionValue }) => {
				localStorage.setItem(storageKey, JSON.stringify(sessionValue));
			},
			{ storageKey: STORAGE_KEY, sessionValue: DEMO_SESSION }
		);

		const report = [];
		await runAuthSmokeCheck(browser);

		for (const route of ROUTES) {
			const page = await context.newPage();
			const failedRequests = [];
			const apiResponses = [];
			const pendingApiRequests = new Set();
			let routeError = '';

			page.setDefaultTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);
			page.setDefaultNavigationTimeout(ROUTE_NAVIGATION_TIMEOUT_MS);

			page.on('requestfailed', (request) => {
				const url = request.url();
				pendingApiRequests.delete(request.url());
				if (!url.startsWith(API_BASE_URL)) {
					return;
				}

				failedRequests.push({
					method: request.method(),
					url: labelForUrl(url),
					error: request.failure()?.errorText ?? 'request failed'
				});
			});

			page.on('response', (response) => {
				const url = response.url();
				if (!url.startsWith(API_BASE_URL)) {
					return;
				}

				apiResponses.push({
					status: response.status(),
					url: labelForUrl(url)
				});

				if (response.status() >= 400) {
					failedRequests.push({
						method: response.request().method(),
						url: labelForUrl(url),
						error: `HTTP ${response.status()}`
					});
				}
			});

			page.on('request', (request) => {
				if (request.url().startsWith(API_BASE_URL)) {
					pendingApiRequests.add(request.url());
				}
			});

			page.on('requestfinished', (request) => {
				pendingApiRequests.delete(request.url());
			});

			try {
				await page.goto(`${BASE_URL}${route}`, { waitUntil: 'domcontentloaded', timeout: ROUTE_NAVIGATION_TIMEOUT_MS });
				await page.waitForLoadState('networkidle', { timeout: ROUTE_SETTLE_TIMEOUT_MS }).catch(() => {});
				await waitForApiRequestsToSettle(page, pendingApiRequests, ROUTE_SETTLE_TIMEOUT_MS * 4);
				await page.waitForFunction(() => !document.body.innerText.includes('Anonymous'), { timeout: ROUTE_SETTLE_TIMEOUT_MS * 2 }).catch(() => {});
				if (route === '/heatmap') {
					await page
						.waitForFunction(
							() => document.body.innerText.includes('Density canvas') || document.body.innerText.includes('Failed to fetch'),
							{ timeout: ROUTE_SETTLE_TIMEOUT_MS * 4 }
						)
						.catch(() => {});
				}
				await page.waitForTimeout(250);

				if (CAPTURE_SCREENSHOTS) {
					await page.screenshot({
						path: path.join(SCREENSHOT_DIR, routeScreenshotName(route)),
						fullPage: true
					});
				}
			} catch (error) {
				routeError = error instanceof Error ? error.message : String(error);
			}

			const stats = routeError
				? {
					linkCount: 0,
					buttonCount: 0,
					primaryNavLinkCount: 0,
					primaryNavLinks: [],
					topLinks: [],
					topButtons: [],
					surfacePanelCount: 0,
					sectionBlockCount: 0,
					infoBubbleCount: 0,
					tableCount: 0,
					tableRowCount: 0,
					headings: [],
					emptyStates: [],
					keyMetrics: [],
					pageTitle: `route failed: ${routeError}`,
					currentHeading: '',
					routeError
				}
				: await collectRouteStats(page);
			stats.failedRequests = failedRequests;
			stats.apiResponses = apiResponses;
			stats.routeError = routeError;

			report.push({ route, ...stats });
			await page.close();
		}

		console.log(`UI audit for ${BASE_URL}`);
		console.log(`API base for fetch checks: ${API_BASE_URL}`);
		console.log('');

		for (const entry of report) {
			const warnings = summarizeWarnings(entry);
			console.log(`[${entry.route}] ${entry.pageTitle}`);
			console.log(`  links=${entry.linkCount} (sidebar=${entry.primaryNavLinkCount}) buttons=${entry.buttonCount} panels=${entry.surfacePanelCount} tiles=${entry.sectionBlockCount} tables=${entry.tableCount} rows=${entry.tableRowCount}`);
			if (entry.routeError) {
				console.log(`  error=${entry.routeError}`);
			}
			if (entry.keyMetrics.length > 0) {
				console.log(`  metrics=${entry.keyMetrics.join(' | ')}`);
			}
			if (entry.emptyStates.length > 0) {
				console.log(`  states=${entry.emptyStates.join(' | ')}`);
			}
			if (entry.failedRequests.length > 0) {
				console.log(`  failed=${entry.failedRequests.map((item) => `${item.method} ${item.url}`).join(' | ')}`);
			}
			if (CAPTURE_SCREENSHOTS) {
				console.log(`  screenshot=${path.join(SCREENSHOT_DIR, routeScreenshotName(entry.route))}`);
			}
			if (warnings.length > 0) {
				console.log(`  flags=${warnings.join(' ; ')}`);
			} else {
				console.log('  flags=none');
			}
			if (entry.topLinks.length > 0) {
				console.log(`  topLinks=${entry.topLinks.join(' | ')}`);
			}
			if (entry.topButtons.length > 0) {
				console.log(`  topButtons=${entry.topButtons.join(' | ')}`);
			}
			console.log('');
		}

		const problemPages = report.filter((entry) => summarizeWarnings(entry).length > 0);
		const fetchFailures = report.flatMap((entry) => entry.failedRequests);

		console.log('Summary');
		console.log(`  pages audited: ${report.length}`);
		console.log(`  pages with warnings: ${problemPages.length}`);
		console.log(`  API request failures: ${fetchFailures.length}`);

		if (fetchFailures.length > 0) {
			console.log(
				`  failed requests: ${fetchFailures.map((item) => `${item.method} ${item.url} (${item.error})`).join(' | ')}`
			);
		}
	} finally {
		clearTimeout(stopAt);
		if (browser) {
			await browser.close().catch(() => {});
		}
	}
}

main().catch((error) => {
	console.error(error);
	process.exitCode = 1;
});