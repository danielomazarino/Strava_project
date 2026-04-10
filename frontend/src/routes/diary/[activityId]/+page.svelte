<script lang="ts">
	import { onMount } from 'svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { getActivityDetails } from '$lib/api/activity';
	import type { ActivityDetail } from '$lib/api/models';
	import RoutePreview from '$lib/components/RoutePreview.svelte';

	let activityId = '';
	let loading = true;
	let loadError = '';
	let activity: ActivityDetail | null = null;

	const formatDate = new Intl.DateTimeFormat('en-GB', {
		weekday: 'long',
		day: '2-digit',
		month: 'long',
		year: 'numeric'
	});

	const formatTime = new Intl.DateTimeFormat('en-GB', {
		hour: '2-digit',
		minute: '2-digit'
	});

	function formatDistance(distance: number | null): string {
		if (distance == null) {
			return 'Distance unavailable';
		}

		return `${(distance / 1000).toFixed(1)} km`;
	}

	function formatDuration(seconds: number | null): string {
		if (seconds == null) {
			return 'Unknown';
		}

		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		const remainder = seconds % 60;
		return [hours > 0 ? `${hours}h` : null, `${minutes}m`, `${remainder}s`].filter(Boolean).join(' ');
	}

	function formatMetric(value: number | null, suffix: string): string {
		if (value == null) {
			return 'Unavailable';
		}

		return `${new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 }).format(value)} ${suffix}`;
	}

	onMount(async () => {
		activityId = window.location.pathname.split('/').filter(Boolean).pop() ?? '';
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;

		try {
			const response = await getActivityDetails(athleteId, Number(activityId));
			activity = response.activity;
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Unable to load activity detail';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Activity detail</title>
</svelte:head>

<section class="surface-panel">
	<div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
		<div>
			<p class="label-sharp">Activity detail</p>
			<h1 class="section-title mt-2 text-3xl md:text-4xl">Detailed activity view</h1>
			<p class="section-subtitle">Metrics, notes, and route preview from the imported Strava polyline.</p>
		</div>
		<a class="action-button action-button--secondary" href="/diary">Back to diary</a>
	</div>

	{#if loading}
		<div class="mt-6 grid gap-4 md:grid-cols-2">
			<div class="surface-panel min-h-40 animate-pulse"></div>
			<div class="surface-panel min-h-40 animate-pulse"></div>
		</div>
	{:else if loadError}
		<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">
			<p class="font-semibold">Unable to load activity</p>
			<p class="mt-2">{loadError}</p>
		</div>
	{:else if activity}
		<div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
			<div class="section-block">
				<p class="label-sharp">Distance</p>
				<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{formatDistance(activity.distance)}</p>
			</div>
			<div class="section-block">
				<p class="label-sharp">Moving time</p>
				<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{formatDuration(activity.moving_time)}</p>
			</div>
			<div class="section-block">
				<p class="label-sharp">Elevation</p>
				<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{formatMetric(activity.elevation_gain, 'm')}</p>
			</div>
			<div class="section-block">
				<p class="label-sharp">Time</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{formatDate.format(new Date(activity.start_date))}</p>
				<p class="mt-1 text-sm leading-6 text-[var(--color-text-muted)]">{formatTime.format(new Date(activity.start_date))}</p>
			</div>
		</div>

		<div class="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
			<div class="section-block">
				<p class="label-sharp">Overview</p>
				<h2 class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)] md:text-3xl">{activity.name ?? `Activity ${activity.strava_activity_id}`}</h2>
				<div class="mt-4 flex flex-wrap gap-2 text-sm text-[var(--color-text-muted)]">
					<span class="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1">{activity.type ?? 'Activity'}</span>
					<span class="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1">{activity.location_country ?? 'Global'}</span>
					<span class="rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1">{activity.timezone ?? 'Timezone unknown'}</span>
				</div>
				<p class="mt-5 text-sm leading-7 text-[var(--color-text-muted)]">{activity.description ?? 'No notes were attached to this activity.'}</p>
			</div>

			<div class="section-block">
				<p class="label-sharp">Training context</p>
				<ul class="bullet-list mt-4">
					<li>This space is reserved for future charts, summary insights, and route comparisons.</li>
					<li>The detail route already has the data plumbing needed for later passes.</li>
				</ul>
			</div>
		</div>

		<div class="mt-6">
			<RoutePreview polyline={activity.polyline} />
		</div>
		{#if $session}
			<div class="mt-6 section-block">
				<p class="label-sharp">Connected athlete</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{$session.stravaAthleteId}</p>
			</div>
		{/if}
	{/if}
</section>