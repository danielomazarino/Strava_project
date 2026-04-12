<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { getSessionAthleteId, session } from '$lib/stores/session';
	import { listDiaryEntries } from '$lib/api/diary';
	import type { DiaryEntry } from '$lib/api/models';

	let loading = true;
	let error = '';
	let entries: DiaryEntry[] = [];

	const formatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

	function summarize(entriesToSummarize: DiaryEntry[]) {
		return entriesToSummarize.reduce(
			(accumulator, entry) => {
				accumulator.distance += entry.distance ?? 0;
				accumulator.time += entry.moving_time ?? 0;
				accumulator.elevation += entry.elevation_gain ?? 0;
				accumulator.count += 1;
				return accumulator;
			},
			{ distance: 0, time: 0, elevation: 0, count: 0 }
		);
	}

	function getWindow(entriesToFilter: DiaryEntry[], daysBack: number) {
		const now = new Date();
		const start = new Date(now);
		start.setDate(start.getDate() - daysBack);
		return entriesToFilter.filter((entry) => {
			const date = new Date(entry.start_date);
			return date >= start && date <= now;
		});
	}

	function trendLabel(currentValue: number, previousValue: number) {
		if (previousValue === 0) {
			return 'No prior period';
		}
		const change = ((currentValue - previousValue) / previousValue) * 100;
		return change >= 0 ? `Up ${Math.abs(change).toFixed(0)}% vs previous period` : `Down ${Math.abs(change).toFixed(0)}% vs previous period`;
	}

	onMount(async () => {
		const athleteId = getSessionAthleteId($session);
		if (athleteId) {
			try {
				const response = await listDiaryEntries(athleteId);
				entries = response.entries;
			} catch (caught) {
				error = caught instanceof Error ? caught.message : 'Unable to load dashboard';
			}
		} else {
			error = 'Connect Strava to load the dashboard. Explicit demo sessions are no longer loaded automatically.';
		}
		loading = false;
	});

	$: weeklySummary = summarize(getWindow(entries, 7));
	$: previousWeeklySummary = summarize(getWindow(entries, 14).slice(0, Math.max(getWindow(entries, 14).length - getWindow(entries, 7).length, 0)));
	$: monthlySummary = summarize(getWindow(entries, 30));
	$: recentEntries = entries.slice(0, 5);
</script>

<svelte:head>
	<title>Dashboard</title>
</svelte:head>

<PageShell title="Dashboard" subtitle="Your training at a glance">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Overview</p>
				<h2 class="section-title mt-2">Seven-day training snapshot</h2>
				<p class="section-subtitle">A compact readout of the most recent week and the broader monthly trend.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<a class="action-button action-button--secondary" href="/diary">Open diary</a>
				<a class="action-button action-button--secondary" href="/compare">Compare sessions</a>
			</div>
		</div>

		{#if loading}
			<div class="mt-6 grid gap-4 lg:grid-cols-2">
				<div class="surface-panel min-h-28 animate-pulse"></div>
				<div class="surface-panel min-h-28 animate-pulse"></div>
			</div>
		{:else if error}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
		{:else}
			<div class="mt-6 grid gap-4 lg:grid-cols-2">
				<section class="section-block">
					<p class="label-sharp">Week</p>
					<dl class="mt-4 grid gap-4 sm:grid-cols-2">
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Distance</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{formatter.format(weeklySummary.distance / 1000)} km</dd>
							<dd class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{trendLabel(weeklySummary.distance, previousWeeklySummary.distance)}</dd>
						</div>
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Time</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{Math.round(weeklySummary.time / 3600)}h {Math.round((weeklySummary.time % 3600) / 60)}m</dd>
							<dd class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{weeklySummary.count} activities</dd>
						</div>
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Elevation</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{formatter.format(weeklySummary.elevation)} m</dd>
						</div>
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Sessions</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{weeklySummary.count}</dd>
							<dd class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Activities this week</dd>
						</div>
					</dl>
				</section>

				<section class="section-block">
					<p class="label-sharp">Month</p>
					<dl class="mt-4 grid gap-4 sm:grid-cols-3">
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Distance</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{formatter.format(monthlySummary.distance / 1000)} km</dd>
						</div>
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Time</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{Math.round(monthlySummary.time / 3600)}h {Math.round((monthlySummary.time % 3600) / 60)}m</dd>
						</div>
						<div>
							<dt class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Elevation</dt>
							<dd class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{formatter.format(monthlySummary.elevation)} m</dd>
						</div>
					</dl>
				</section>
			</div>
		{/if}
	</section>

	<section class="mt-6 surface-panel">
		<p class="label-sharp">Recent activities</p>
			<div class="mt-4 space-y-3">
				{#if loading}
					<div class="space-y-3">
						<div class="surface-panel min-h-20 animate-pulse"></div>
						<div class="surface-panel min-h-20 animate-pulse"></div>
						<div class="surface-panel min-h-20 animate-pulse"></div>
						<div class="surface-panel min-h-20 animate-pulse"></div>
						<div class="surface-panel min-h-20 animate-pulse"></div>
					</div>
				{:else if recentEntries.length === 0}
					<p class="text-sm leading-6 text-[var(--color-text-muted)]">No activities loaded yet. Connect Strava from the sidebar system section to unlock the recent sessions list.</p>
				{:else}
					{#each recentEntries as entry}
						<a class="flex items-center justify-between gap-4 border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 transition hover:border-[var(--color-accent)]" href={`/diary/${entry.strava_activity_id}`}>
							<div>
								<p class="label-sharp">{entry.type ?? 'Activity'}</p>
								<p class="mt-1 text-base font-semibold tracking-tight text-[var(--color-text)]">{entry.name ?? `Activity ${entry.strava_activity_id}`}</p>
							</div>
							<p class="text-xs text-[var(--color-text-muted)]">{formatter.format((entry.distance ?? 0) / 1000)} km · {Math.round((entry.moving_time ?? 0) / 60)} min</p>
						</a>
					{/each}
				{/if}
			</div>
	</section>
</PageShell>
