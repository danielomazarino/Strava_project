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
	let selectedActivityId = '';
	let activity: ActivityDetail | null = null;

	async function loadRouteData() {
		loading = true;
		error = '';
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
		try {
			const response = await listDiaryEntries(athleteId);
			entries = response.entries;
			selectedActivityId = String(entries[0]?.strava_activity_id ?? '');
			if (selectedActivityId) {
				activity = (await getActivityDetails(athleteId, Number(selectedActivityId))).activity;
			}
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Unable to load routes';
		} finally {
			loading = false;
		}
	}

	async function selectActivity(activityId: string) {
		selectedActivityId = activityId;
		if (activityId) {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			activity = (await getActivityDetails(athleteId, Number(activityId))).activity;
		}
	}

	onMount(() => {
		void loadRouteData();
	});
</script>

<svelte:head>
	<title>Routes</title>
</svelte:head>

<PageShell title="Routes" subtitle="Select an activity and inspect the route preview.">
	<section class="surface-panel">
		<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Route explorer</p>
				<h2 class="section-title mt-2">Select an activity and inspect the route preview.</h2>
				<p class="section-subtitle">The list stays on the left and the route stays on the right, so distance, shape, and climbing are easy to compare.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void loadRouteData()}>Reload routes</button>
				<a class="action-button action-button--secondary" href="/compare">Compare routes</a>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		{#if loading}
			<div class="surface-panel min-h-72 animate-pulse"></div>
		{:else if error}
			<div class="border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
		{:else}
			<div class="grid gap-6 xl:grid-cols-[minmax(0,0.44fr)_minmax(0,0.56fr)]">
				<div class="section-block">
					<p class="label-sharp">Route list</p>
					<label class="mt-4 flex flex-col gap-2">
						<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Choose activity</span>
						<select bind:value={selectedActivityId} class="input-sharp" on:change={() => void selectActivity(selectedActivityId)}>
							{#each entries.slice(0, 10) as entry}
								<option value={entry.strava_activity_id}>{entry.type ?? 'Activity'} · {entry.name ?? `Activity ${entry.strava_activity_id}`} · {(entry.distance ?? 0) / 1000} km</option>
							{/each}
						</select>
					</label>
					<div class="mt-4 rounded-[1.3rem] border border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] p-4 text-sm leading-6 text-[var(--color-text-muted)]">
						The list is now a single selector so the preview stays the main focus.
					</div>
				</div>

				<div class="surface-panel">
					<p class="label-sharp">Selected activity</p>
					<h3 class="mt-3 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{activity?.name ?? 'Choose an activity'}</h3>
					{#if activity}
						<div class="mt-4 grid gap-3 md:grid-cols-3">
							<div class="section-block"><p class="label-sharp">Distance</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{(activity.distance ? activity.distance / 1000 : 0).toFixed(1)} km</p></div>
							<div class="section-block"><p class="label-sharp">Time</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{Math.round((activity.moving_time ?? 0) / 60)} min</p></div>
							<div class="section-block"><p class="label-sharp">Elevation</p><p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{activity.elevation_gain ?? 0} m</p></div>
						</div>
						<div class="mt-6"><RoutePreview polyline={activity.polyline} /></div>
					{/if}
				</div>
			</div>

			<div class="mt-6 section-block">
				<p class="label-sharp">How to use it</p>
				<ul class="bullet-list mt-4">
					<li>Choose an activity to populate the route preview and the summary bubbles.</li>
					<li>Use Compare routes when you want to check two sessions side by side.</li>
				</ul>
			</div>
		{/if}
	</section>
</PageShell>