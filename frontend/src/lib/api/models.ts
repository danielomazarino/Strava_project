export type ApiStatusResponse = {
	status: 'ok';
};

export type DiaryEntry = {
	id: string;
	strava_activity_id: number;
	name: string | null;
	type: string | null;
	start_date: string;
	distance: number | null;
	moving_time: number | null;
	elapsed_time: number | null;
	elevation_gain: number | null;
	description: string | null;
	location_country: string | null;
};

export type SearchResult = {
	id: string;
	strava_activity_id: number;
	name: string | null;
	type: string | null;
	start_date: string;
	score: number | null;
};

export type SummaryInsight = {
	summary: string;
	volume: string | null;
	intensity: string | null;
	notable_events: string[];
	subjective_notes: string[];
	performance_patterns: string[];
};

export type PatternInsight = {
	patterns: string[];
	fatigue: string[];
	motivation: string[];
	terrain_effects: string[];
	weather_effects: string[];
	pacing_issues: string[];
};

export type RegionComparisonInsight = {
	region_a: string;
	region_b: string;
	perceived_effort: string;
	terrain_differences: string[];
	pacing_differences: string[];
	subjective_notes: string[];
};

export type ActivityImportResult = {
	status: 'ok';
	imported: number;
};

export type ActivityDetail = {
	id: string;
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
	raw_payload: Record<string, unknown> | null;
	created_at: string | null;
	updated_at: string | null;
};

export type TokenHealth = 'active' | 'expiring' | 'expired';

export type GeoPoint = {
	lat: number;
	lng: number;
};

export type GeoBounds = {
	min_lat: number;
	min_lng: number;
	max_lat: number;
	max_lng: number;
};

export type HeatmapTilePoint = {
	activity_id: string;
	strava_activity_id: number;
	lat: number;
	lng: number;
};

export type HeatmapTile = {
	z: number;
	x: number;
	y: number;
	point_count: number;
	activity_count: number;
	bounds: GeoBounds;
	generated_at: string;
	points: HeatmapTilePoint[];
};

export type HeatmapResponse = {
	status: 'ok';
	tile: HeatmapTile;
};