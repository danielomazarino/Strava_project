import type {
	ActivityImportResult,
	ActivityDetail,
	ApiStatusResponse,
	TokenHealth,
	DiaryEntry,
	HeatmapResponse,
	HeatmapTile,
	PatternInsight,
	RegionComparisonInsight,
	SearchResult,
	SummaryInsight
} from './models';

type DemoActivity = DiaryEntry & ActivityDetail;

type DemoAdminUser = {
	id: string;
	strava_athlete_id: number;
	token_expires_at: string;
	token_health: TokenHealth;
	activity_count: number;
	latest_activity_start_date: string | null;
	latest_activity_name: string | null;
	latest_activity_country: string | null;
};

type DemoAdminActivity = {
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
	raw_payload: Record<string, unknown> | null;
	created_at: string | null;
	updated_at: string | null;
};

const demoPolyline = '_leiI_y|u@owHowHowHowH~{BowH~uJowH';
const demoAthleteId = 14706324;
const demoUserId = 'demo-user';
const demoGeneratedAt = new Date().toISOString();

type DemoSeed = {
	daysAgo: number;
	stravaActivityId: number;
	name: string;
	type: string;
	distance: number;
	movingTime: number;
	elapsedTime: number;
	elevationGain: number;
	description: string;
	locationCountry: string;
	timezone: string;
	polyline: string;
};

const demoSeeds: DemoSeed[] = [
	{
		daysAgo: 1,
		stravaActivityId: 9000101,
		name: 'Threshold Run',
		type: 'Run',
		distance: 11200,
		movingTime: 3480,
		elapsedTime: 3560,
		elevationGain: 118,
		description: 'Steady threshold block with a controlled final kilometer.',
		locationCountry: 'GB',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 3,
		stravaActivityId: 9000102,
		name: 'Recovery Spin',
		type: 'Ride',
		distance: 28100,
		movingTime: 4860,
		elapsedTime: 5010,
		elevationGain: 240,
		description: 'Easy cycling with low intensity and mostly flat terrain.',
		locationCountry: 'SE',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 5,
		stravaActivityId: 9000103,
		name: 'Hills Session',
		type: 'Run',
		distance: 15600,
		movingTime: 4860,
		elapsedTime: 4940,
		elevationGain: 312,
		description: 'Hill repeats and progression work on rolling roads.',
		locationCountry: 'GB',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 7,
		stravaActivityId: 9000104,
		name: 'Long Ride',
		type: 'Ride',
		distance: 53200,
		movingTime: 8580,
		elapsedTime: 8790,
		elevationGain: 435,
		description: 'Long endurance ride with a late push into the final section.',
		locationCountry: 'SE',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 10,
		stravaActivityId: 9000105,
		name: 'Easy Morning Run',
		type: 'Run',
		distance: 8400,
		movingTime: 2880,
		elapsedTime: 2940,
		elevationGain: 64,
		description: 'Short aerobic run before work with relaxed pacing.',
		locationCountry: 'FR',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 14,
		stravaActivityId: 9000106,
		name: 'Tempo Loop',
		type: 'Run',
		distance: 18300,
		movingTime: 5820,
		elapsedTime: 5910,
		elevationGain: 146,
		description: 'Tempo efforts on a looped route with a strong closing segment.',
		locationCountry: 'GB',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 18,
		stravaActivityId: 9000107,
		name: 'City Cruise',
		type: 'Ride',
		distance: 21400,
		movingTime: 3720,
		elapsedTime: 3810,
		elevationGain: 92,
		description: 'Short city ride with quick stops and light traffic.',
		locationCountry: 'SE',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 21,
		stravaActivityId: 9000108,
		name: 'Long Run',
		type: 'Run',
		distance: 22400,
		movingTime: 7680,
		elapsedTime: 7750,
		elevationGain: 220,
		description: 'Long run with a smooth second half and steady effort.',
		locationCountry: 'GB',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 26,
		stravaActivityId: 9000109,
		name: 'Trail Session',
		type: 'Run',
		distance: 13300,
		movingTime: 4980,
		elapsedTime: 5120,
		elevationGain: 358,
		description: 'Trail routes with technical terrain and stronger climbing.',
		locationCountry: 'NO',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	},
	{
		daysAgo: 33,
		stravaActivityId: 9000110,
		name: 'Progression Ride',
		type: 'Ride',
		distance: 41200,
		movingTime: 6480,
		elapsedTime: 6630,
		elevationGain: 278,
		description: 'Ride that builds steadily from easy to moderate effort.',
		locationCountry: 'DK',
		timezone: 'Europe/Stockholm',
		polyline: demoPolyline
	}
];

function dayOffset(daysAgo: number): Date {
	const date = new Date();
	date.setHours(9, 0, 0, 0);
	date.setDate(date.getDate() - daysAgo);
	return date;
}

function buildActivity(seed: DemoSeed): DemoActivity {
	const startDate = dayOffset(seed.daysAgo).toISOString();

	return {
		id: `demo-${seed.stravaActivityId}`,
		strava_activity_id: seed.stravaActivityId,
		name: seed.name,
		type: seed.type,
		start_date: startDate,
		distance: seed.distance,
		moving_time: seed.movingTime,
		elapsed_time: seed.elapsedTime,
		elevation_gain: seed.elevationGain,
		description: seed.description,
		location_country: seed.locationCountry,
		polyline: seed.polyline,
		timezone: seed.timezone,
	raw_payload: {
		id: seed.stravaActivityId,
		name: seed.name,
		type: seed.type,
		description: seed.description,
		location_country: seed.locationCountry
	},
	created_at: startDate,
	updated_at: startDate
	};
}

function getActivities(): DemoActivity[] {
	return demoSeeds.map(buildActivity).sort((left, right) => right.start_date.localeCompare(left.start_date));
}

function scoreSearchResult(activity: DemoActivity, queryText: string): number {
	const normalizedQuery = queryText.trim().toLowerCase();
	if (!normalizedQuery) {
		return 0;
	}

	const haystack = [activity.name, activity.type, activity.description, activity.location_country].filter(Boolean).join(' ').toLowerCase();
	const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
	return tokens.reduce((score, token) => score + (haystack.includes(token) ? 1 : 0), 0);
}

function getSearchResults(queryText: string): SearchResult[] {
	return getActivities()
		.map((activity) => ({
			id: activity.id,
			strava_activity_id: activity.strava_activity_id,
			name: activity.name,
			type: activity.type,
			start_date: activity.start_date,
			score: scoreSearchResult(activity, queryText)
		}))
		.filter((result) => result.score && result.score > 0)
		.sort((left, right) => (right.score ?? 0) - (left.score ?? 0))
		.slice(0, 6);
}

function summarizeWindow(entries: DemoActivity[]): SummaryInsight {
	const totalDistance = entries.reduce((sum, entry) => sum + (entry.distance ?? 0), 0);
	const totalMovingTime = entries.reduce((sum, entry) => sum + (entry.moving_time ?? 0), 0);
	return {
		summary: 'Demo mode shows a steady blend of running and riding with one long-session block every week.',
		volume: `${(totalDistance / 1000).toFixed(1)} km across ${entries.length} sessions`,
		intensity: `${Math.round(totalMovingTime / 60)} minutes of movement in the selected range`,
		notable_events: ['Tempo work is clustered in the middle of the block.', 'Ride volume is enough to show a clear secondary training line.'],
		subjective_notes: ['The archive looks consistent rather than spiky.', 'Recovery days separate the harder sessions cleanly.'],
		performance_patterns: ['Long runs sit near the weekend.', 'Climbing is strongest on the trail and hill days.']
	};
}

function patternSignals(entries: DemoActivity[]): PatternInsight {
	return {
		patterns: ['A weekly long session remains visible in the demo block.', 'Pace settles after a hard day and stays controlled.'],
		fatigue: ['Recovery spin follows the hardest run.', 'The easy days are spaced well around the long work.'],
		motivation: ['The archive keeps a strong weekly rhythm.', 'There is enough variation to make the training feel dynamic.'],
		terrain_effects: ['Trail work adds more elevation than the road sessions.', 'Hill days are the clearest outlier for climbing.'],
		weather_effects: ['Weather data is not part of the demo dataset.', 'Use the full backend-backed view for real conditions.'],
		pacing_issues: ['No obvious pacing breakdowns in this sample.', 'Tempo sessions are the most useful for comparison.']
	};
}

function compareRegions(regionA: string, regionB: string): RegionComparisonInsight {
	return {
		region_a: regionA,
		region_b: regionB,
		perceived_effort: `${regionA} feels smoother in the demo sample, while ${regionB} carries more climbing pressure.`,
		terrain_differences: [`${regionA} shows flatter route lines in the sample.`, `${regionB} has more rolling terrain and punchier climbs.`],
		pacing_differences: [`${regionA} supports steadier pacing.`, `${regionB} pushes effort harder on the climbs.`],
		subjective_notes: ['This is demo copy, not a real analysis.', 'Replace with the live model output once the backend is available.']
	};
}

function buildAdminOverview(): {
	status: 'ok';
	generated_at: string;
	totals: {
		users: number;
		activities: number;
		active_tokens: number;
		expiring_tokens: number;
		expired_tokens: number;
	};
	users: DemoAdminUser[];
	recent_activities: DemoAdminActivity[];
	records: DemoAdminActivity[];
} {
	const activities = getActivities();
	const users: DemoAdminUser[] = [
		{
			id: 'demo-user',
			strava_athlete_id: demoAthleteId,
			token_expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
			token_health: 'active',
			activity_count: activities.length,
			latest_activity_start_date: activities[0]?.start_date ?? null,
			latest_activity_name: activities[0]?.name ?? null,
			latest_activity_country: activities[0]?.location_country ?? null
		}
	];

	const recent_activities: DemoAdminActivity[] = activities.slice(0, 8).map((activity) => ({
		id: activity.id,
		user_id: demoUserId,
		user_strava_athlete_id: demoAthleteId,
		strava_activity_id: activity.strava_activity_id,
		name: activity.name,
		type: activity.type,
		start_date: activity.start_date,
		distance: activity.distance,
		moving_time: activity.moving_time,
		elapsed_time: activity.elapsed_time,
		elevation_gain: activity.elevation_gain,
		description: activity.description,
		polyline: activity.polyline,
		timezone: activity.timezone,
		location_country: activity.location_country,
		has_raw_payload: true,
		raw_payload: {
			id: activity.strava_activity_id,
			name: activity.name,
			type: activity.type,
			description: activity.description,
			location_country: activity.location_country
		},
		created_at: activity.start_date,
		updated_at: activity.start_date
	}));

	return {
		status: 'ok',
		generated_at: demoGeneratedAt,
		totals: {
			users: 1,
			activities: activities.length,
			active_tokens: 1,
			expiring_tokens: 0,
			expired_tokens: 0
		},
		users,
		recent_activities,
		records: recent_activities
	};
}

function buildHeatmapTile(z: number, x: number, y: number): HeatmapTile {
	const centerLat = 57.7089;
	const centerLng = 11.9746;
	const spread = Math.max(0.02 / Math.max(z, 1), 0.002);
	const points = Array.from({ length: 18 }, (_, index) => {
		const offset = (index - 9) / 9;
		return {
			activity_id: `demo-${9000101 + index}`,
			strava_activity_id: 9000101 + index,
			lat: centerLat + offset * spread * 2,
			lng: centerLng + Math.sin(index) * spread * 2
		};
	});

	return {
		z,
		x,
		y,
		point_count: points.length,
		activity_count: 9,
		bounds: {
			min_lat: centerLat - spread * 3,
			min_lng: centerLng - spread * 3,
			max_lat: centerLat + spread * 3,
			max_lng: centerLng + spread * 3
		},
		generated_at: demoGeneratedAt,
		points
	};
}

function extractSearchQuery(path: string): string {
	const url = new URL(path, 'http://demo.local');
	return url.searchParams.get('q') ?? '';
}

function extractDateRange(path: string): { startDate: string | null; endDate: string | null } {
	const url = new URL(path, 'http://demo.local');
	return {
		startDate: url.searchParams.get('start_date'),
		endDate: url.searchParams.get('end_date')
	};
}

function getEntriesForRange(startDate: string | null, endDate: string | null): DemoActivity[] {
	const entries = getActivities();
	if (!startDate && !endDate) {
		return entries;
	}

	const start = startDate ? new Date(startDate) : new Date('2000-01-01T00:00:00Z');
	const end = endDate ? new Date(endDate) : new Date('2100-01-01T00:00:00Z');
	return entries.filter((entry) => {
		const entryDate = new Date(entry.start_date);
		return entryDate >= start && entryDate <= end;
	});
}

export function getDemoApiResponse(path: string): unknown {
	const url = new URL(path, 'http://demo.local');
	const { pathname } = url;

	if (pathname === '/diary') {
		const athleteId = Number(url.searchParams.get('strava_athlete_id') ?? demoAthleteId);
		void athleteId;
		return {
			status: 'ok',
			entries: getActivities()
		};
	}

	if (pathname.startsWith('/activities/') && pathname !== '/activities/import') {
		const stravaActivityId = Number(pathname.split('/').pop());
		const activity = getActivities().find((entry) => entry.strava_activity_id === stravaActivityId) ?? getActivities()[0];
		return {
			status: 'ok',
			activity
		};
	}

	if (pathname === '/search/keyword' || pathname === '/search/semantic') {
		const queryText = extractSearchQuery(path);
		return {
			status: 'ok',
			results: getSearchResults(queryText)
		};
	}

	if (pathname === '/insights/summary') {
		const { startDate, endDate } = extractDateRange(path);
		return {
			status: 'ok',
			analysis: summarizeWindow(getEntriesForRange(startDate, endDate))
		};
	}

	if (pathname === '/insights/patterns') {
		const { startDate, endDate } = extractDateRange(path);
		return {
			status: 'ok',
			analysis: patternSignals(getEntriesForRange(startDate, endDate))
		};
	}

	if (pathname === '/insights/regions/comparison') {
		const regionA = url.searchParams.get('region_a') ?? 'GB';
		const regionB = url.searchParams.get('region_b') ?? 'SE';
		return {
			status: 'ok',
			analysis: compareRegions(regionA, regionB)
		};
	}

	if (pathname.startsWith('/heatmaps/tiles/')) {
		const [, , , zString, xString, yString] = pathname.split('/');
		return {
			status: 'ok',
			tile: buildHeatmapTile(Number(zString), Number(xString), Number(yString))
		} satisfies HeatmapResponse;
	}

	if (pathname === '/activities/import') {
		return {
			status: 'ok',
			imported: getActivities().length
		} satisfies ActivityImportResult;
	}

	if (pathname === '/admin/overview') {
		return buildAdminOverview() satisfies ApiStatusResponse & {
			generated_at: string;
			totals: {
				users: number;
				activities: number;
				active_tokens: number;
				expiring_tokens: number;
				expired_tokens: number;
			};
			users: DemoAdminUser[];
			recent_activities: DemoAdminActivity[];
		};
	}

	throw new Error(`No demo response configured for ${pathname}`);
}