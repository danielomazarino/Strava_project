<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { listDiaryEntries } from '$lib/api/diary';
	import { getActivityDetails } from '$lib/api/activity';
	import RoutePreview from '$lib/components/RoutePreview.svelte';
	import type { ActivityDetail, DiaryEntry } from '$lib/api/models';

	let loading = true;
	let error = '';
	let entries: DiaryEntry[] = [];
	let leftId = '';
	let rightId = '';
	let left: ActivityDetail | null = null;
	let right: ActivityDetail | null = null;

	async function loadActivities() {
		try {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			entries = (await listDiaryEntries(athleteId)).entries;
			leftId = String(entries[0]?.strava_activity_id ?? '');
			rightId = String(entries[1]?.strava_activity_id ?? entries[0]?.strava_activity_id ?? '');
			if (leftId) left = (await getActivityDetails(athleteId, Number(leftId))).activity;
			if (rightId) right = (await getActivityDetails(athleteId, Number(rightId))).activity;
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Unable to load comparison data';
		} finally {
			loading = false;
		}
	}

	async function updatePair() {
		if (leftId && rightId) {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			left = (await getActivityDetails(athleteId, Number(leftId))).activity;
			right = (await getActivityDetails(athleteId, Number(rightId))).activity;
		}
	}

	async function swapPair() {
		const previousLeft = leftId;
		leftId = rightId;
		rightId = previousLeft;
		await updatePair();
	}

	onMount(() => {
		void loadActivities();
	});
</script>

<svelte:head>
	<title>Compare</title>
</svelte:head>

<PageShell title="Compare" subtitle="Place two activities side by side.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Side-by-side analysis</p>
				<h2 class="section-title mt-2">Pick two sessions and compare the training shape.</h2>
				<p class="section-subtitle">Use the selectors to pair sessions, then read the route, distance, and elevation differences side by side.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void updatePair()}>Refresh pair</button>
				<button class="action-button action-button--secondary" on:click={() => void swapPair()}>Swap pair</button>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		<p class="label-sharp">Activity selectors</p>
		<div class="mt-4 grid gap-3 md:grid-cols-2">
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Left activity</span>
				<select bind:value={leftId} class="input-sharp" on:change={updatePair}>{#each entries as entry}<option value={entry.strava_activity_id}>{entry.name ?? `Activity ${entry.strava_activity_id}`}</option>{/each}</select>
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Right activity</span>
				<select bind:value={rightId} class="input-sharp" on:change={updatePair}>{#each entries as entry}<option value={entry.strava_activity_id}>{entry.name ?? `Activity ${entry.strava_activity_id}`}</option>{/each}</select>
			</label>
		</div>

		{#if loading}
			<div class="mt-6 grid gap-4 md:grid-cols-2">
				<div class="surface-panel min-h-72 animate-pulse"></div>
				<div class="surface-panel min-h-72 animate-pulse"></div>
			</div>
		{:else if error}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
		{:else}
			<div class="mt-6 grid gap-4 xl:grid-cols-2">
				<article class="section-block">
					<p class="label-sharp">Left</p>
					<h3 class="mt-3 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{left?.name ?? 'Choose activity'}</h3>
					{#if left}
						<div class="mt-4 grid gap-3 sm:grid-cols-3">
							<div><p class="label-sharp">Distance</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{((left.distance ?? 0) / 1000).toFixed(1)} km</p></div>
							<div><p class="label-sharp">Time</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{Math.round((left.moving_time ?? 0) / 60)} min</p></div>
							<div><p class="label-sharp">Elevation</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{left.elevation_gain ?? 0} m</p></div>
						</div>
						<div class="mt-4"><RoutePreview polyline={left.polyline} /></div>
					{/if}
				</article>
				<article class="section-block">
					<p class="label-sharp">Right</p>
					<h3 class="mt-3 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{right?.name ?? 'Choose activity'}</h3>
					{#if right}
						<div class="mt-4 grid gap-3 sm:grid-cols-3">
							<div><p class="label-sharp">Distance</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{((right.distance ?? 0) / 1000).toFixed(1)} km</p></div>
							<div><p class="label-sharp">Time</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{Math.round((right.moving_time ?? 0) / 60)} min</p></div>
							<div><p class="label-sharp">Elevation</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{right.elevation_gain ?? 0} m</p></div>
						</div>
						<div class="mt-4"><RoutePreview polyline={right.polyline} /></div>
					{/if}
				</article>
			</div>

			<div class="mt-6 section-block">
				<p class="label-sharp">What the comparison shows</p>
				<ul class="bullet-list mt-4">
					<li>Distance and duration tell you how big the sessions really were.</li>
					<li>Route previews help you understand whether the effort came from terrain or pacing.</li>
					<li>Swap the pair when you want to compare the same athlete across different weeks.</li>
				</ul>
			</div>
		{/if}
	</section>
</PageShell>