import type { DiaryEntry } from '$lib/api/models';

export type Bucket = {
	label: string;
	count: number;
	distance: number;
};

export type PaceBucket = {
	label: string;
	count: number;
};

export type TrendSummary = {
	activityCount: number;
	totalDistance: number;
	totalMovingTime: number;
	averageDistance: number;
	averagePace: number | null;
	activeDays: number;
	longestStreak: number;
};

function normalizeDate(date: Date): string {
	return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
}

export function formatWeekLabel(date: Date): string {
	const year = date.getUTCFullYear();
	const month = String(date.getUTCMonth() + 1).padStart(2, '0');
	const day = String(date.getUTCDate()).padStart(2, '0');
	return `${year}-${month}-${day}`;
}

export function groupByWeek(entries: DiaryEntry[]): Bucket[] {
	const buckets = new Map<string, Bucket>();

	for (const entry of entries) {
		const date = new Date(entry.start_date);
		const start = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
		start.setUTCDate(start.getUTCDate() - ((start.getUTCDay() + 6) % 7));
		const label = formatWeekLabel(start);
		const bucket = buckets.get(label) ?? { label, count: 0, distance: 0 };
		bucket.count += 1;
		bucket.distance += entry.distance ?? 0;
		buckets.set(label, bucket);
	}

	return [...buckets.values()].sort((left, right) => left.label.localeCompare(right.label));
}

export function groupByMonth(entries: DiaryEntry[]): Bucket[] {
	const buckets = new Map<string, Bucket>();

	for (const entry of entries) {
		const date = new Date(entry.start_date);
		const label = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
		const bucket = buckets.get(label) ?? { label, count: 0, distance: 0 };
		bucket.count += 1;
		bucket.distance += entry.distance ?? 0;
		buckets.set(label, bucket);
	}

	return [...buckets.values()].sort((left, right) => left.label.localeCompare(right.label));
}

export function paceSecondsPerKilometre(entry: DiaryEntry): number | null {
	if (!entry.distance || !entry.moving_time) {
		return null;
	}

	return entry.moving_time / (entry.distance / 1000);
}

export function formatPace(secondsPerKilometre: number | null): string {
	if (secondsPerKilometre == null || !Number.isFinite(secondsPerKilometre)) {
		return 'n/a';
	}

	const minutes = Math.floor(secondsPerKilometre / 60);
	const seconds = Math.round(secondsPerKilometre % 60);
	return `${minutes}:${String(seconds).padStart(2, '0')} /km`;
}

export function paceBucketLabel(secondsPerKilometre: number | null): string {
	if (secondsPerKilometre == null) {
		return 'Unknown';
	}
	if (secondsPerKilometre < 240) {
		return '< 4:00';
	}
	if (secondsPerKilometre < 300) {
		return '4:00 - 4:59';
	}
	if (secondsPerKilometre < 360) {
		return '5:00 - 5:59';
	}
	if (secondsPerKilometre < 420) {
		return '6:00 - 6:59';
	}
	return '7:00+';
}

export function paceBuckets(entries: DiaryEntry[]): PaceBucket[] {
	const labels = ['< 4:00', '4:00 - 4:59', '5:00 - 5:59', '6:00 - 6:59', '7:00+', 'Unknown'];
	const buckets = new Map(labels.map((label) => [label, 0]));

	for (const entry of entries) {
		const label = paceBucketLabel(paceSecondsPerKilometre(entry));
		buckets.set(label, (buckets.get(label) ?? 0) + 1);
	}

	return labels.map((label) => ({ label, count: buckets.get(label) ?? 0 }));
}

export function summarizeTrends(entries: DiaryEntry[]): TrendSummary {
	const activityCount = entries.length;
	const totalDistance = entries.reduce((sum, entry) => sum + (entry.distance ?? 0), 0);
	const totalMovingTime = entries.reduce((sum, entry) => sum + (entry.moving_time ?? 0), 0);
	const activeDays = new Set(entries.map((entry) => normalizeDate(new Date(entry.start_date)))).size;
	const sortedDays = [...new Set(entries.map((entry) => normalizeDate(new Date(entry.start_date))))].sort();

	let longestStreak = 0;
	let currentStreak = 0;
	let previousDate: Date | null = null;
	for (const day of sortedDays) {
		const currentDate = new Date(`${day}T00:00:00Z`);
		if (previousDate == null) {
			currentStreak = 1;
		} else {
			const diffDays = Math.round((currentDate.getTime() - previousDate.getTime()) / 86400000);
			currentStreak = diffDays === 1 ? currentStreak + 1 : 1;
		}
		longestStreak = Math.max(longestStreak, currentStreak);
		previousDate = currentDate;
	}

	return {
		activityCount,
		totalDistance,
		totalMovingTime,
		averageDistance: activityCount === 0 ? 0 : totalDistance / activityCount,
		averagePace: totalMovingTime > 0 && totalDistance > 0 ? totalMovingTime / (totalDistance / 1000) : null,
		activeDays,
		longestStreak
	};
}