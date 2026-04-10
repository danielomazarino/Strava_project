<script lang="ts">
	import { onMount } from 'svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { listDiaryEntries } from '$lib/api/diary';
	import { semanticSearch } from '$lib/api/search';
	import type { DiaryEntry, SearchResult } from '$lib/api/models';

	let query = '';
	let loading = false;
	let entries: DiaryEntry[] = [];
	let results: SearchResult[] = [];
	let error = '';

	function buildHeuristicQuery(input: string): { search: string; type: string | null; country: string | null } {
		const normalized = input.toLowerCase();
		const type = normalized.includes('run') ? 'Run' : normalized.includes('ride') ? 'Ride' : null;
		const country = normalized.includes('gb') ? 'GB' : normalized.includes('fr') ? 'FR' : null;
		const search = input.replace(/\b(run|ride|gb|fr|hills?|tempo|long)\b/gi, '').trim() || input;
		return { search, type, country };
	}

	async function applySmartFilter() {
		if (query.trim().length === 0) {
			results = [];
			return;
		}

		loading = true;
		error = '';
		try {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			const heuristic = buildHeuristicQuery(query);
			const entriesById = new Map(entries.map((entry) => [entry.strava_activity_id, entry]));
			const response = await semanticSearch(athleteId, heuristic.search);
			results = response.results.filter((result) => {
				if (heuristic.type && result.type !== heuristic.type) {
					return false;
				}
				if (heuristic.country) {
					const entry = entriesById.get(result.strava_activity_id);
					if ((entry?.location_country ?? '').toLowerCase() !== heuristic.country.toLowerCase()) {
						return false;
					}
				}
				return true;
			});
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Unable to apply smart filters';
		} finally {
			loading = false;
		}
	}

	onMount(async () => {
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
		const response = await listDiaryEntries(athleteId);
		entries = response.entries;
	});
</script>

<svelte:head>
	<title>Smart filters</title>
</svelte:head>

<section class="surface-panel">
	<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
		<div>
			<p class="label-sharp">Smart filters</p>
			<h1 class="section-title mt-2">Filter the archive in one step.</h1>
			<p class="section-subtitle">Natural language terms are converted into a search query plus a few local hints.</p>
		</div>
		<button class="action-button action-button--primary w-fit" on:click={() => void applySmartFilter()}>Apply filters</button>
	</div>

	<div class="mt-6 section-block">
		<label class="flex flex-col gap-2">
			<span class="label-sharp">Query</span>
			<input bind:value={query} class="input-sharp" placeholder="Try 'long run in GB', 'tempo ride', or 'hills last month'" />
		</label>
		<div class="mt-4 flex flex-wrap gap-2">
			{#each ['long run', 'tempo ride', 'GB hills', 'friday run'] as chip}
				<button class="action-button action-button--secondary" on:click={() => (query = chip)}>{chip}</button>
			{/each}
		</div>
	</div>

	{#if loading}
		<div class="mt-6 space-y-3">
			<div class="surface-panel animate-pulse min-h-24"></div>
			<div class="surface-panel animate-pulse min-h-24"></div>
		</div>
	{:else if error}
		<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
	{:else if results.length > 0}
		<div class="mt-6 grid gap-3">
			{#each results as result}
				<a class="section-block block transition hover:border-[var(--color-accent)]" href={`/diary/${result.strava_activity_id}`}>
					<div class="flex flex-wrap items-center justify-between gap-3">
						<p class="label-sharp">Matched activity</p>
						<p class="text-xs text-[var(--color-text-muted)]">score {result.score ?? 0}</p>
					</div>
					<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{result.name ?? `Activity ${result.strava_activity_id}`}</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{result.type ?? 'Activity'}</p>
				</a>
			{/each}
		</div>
	{:else if entries.length > 0}
		<div class="mt-6 section-block">
			<p class="label-sharp">Examples</p>
			<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Run the filter to replace this placeholder with actual matches from the diary archive.</p>
		</div>
	{/if}

	<div class="mt-6 section-block">
		<p class="label-sharp">Heuristics</p>
		<ul class="bullet-list mt-4">
			<li>Natural language hints are translated into a semantic search query.</li>
			<li>There is no dedicated AI filtering backend yet.</li>
			<li>This keeps the UI moving without adding more controls.</li>
		</ul>
	</div>
</section>