<script lang="ts">
	import { onMount } from 'svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { keywordSearch, semanticSearch } from '$lib/api/search';
	import type { SearchResult } from '$lib/api/models';

	let query = '';
	let mode: 'keyword' | 'semantic' = 'keyword';
	let loading = false;
	let error = '';
	let results: SearchResult[] = [];

	async function runSearch() {
		if (query.trim().length === 0) {
			results = [];
			return;
		}

		loading = true;
		error = '';
		try {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			results = mode === 'keyword'
				? (await keywordSearch(athleteId, query)).results
				: (await semanticSearch(athleteId, query)).results;
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Search failed';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		query = 'run';
		void runSearch();
	});
</script>

<svelte:head>
	<title>Search</title>
</svelte:head>

<section class="surface-panel">
	<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
		<div>
			<p class="label-sharp">Search</p>
			<h1 class="section-title mt-2">Search the activity archive.</h1>
			<p class="section-subtitle">Run keyword or semantic lookup against the same compact workspace.</p>
		</div>
		<a class="action-button action-button--secondary w-fit" href="/filters">Open smart filters</a>
	</div>

	<div class="mt-6 grid gap-3 md:grid-cols-[minmax(0,1fr)_180px]">
		<input bind:value={query} class="input-sharp" placeholder="Try 'tempo', 'hills', or 'GB'" />
		<div class="flex gap-2">
			<button class:action-button--primary={mode === 'keyword'} class="action-button action-button--secondary flex-1" on:click={() => (mode = 'keyword')}>Keyword</button>
			<button class:action-button--primary={mode === 'semantic'} class="action-button action-button--secondary flex-1" on:click={() => (mode = 'semantic')}>Semantic</button>
		</div>
	</div>

	<div class="mt-4 flex flex-wrap gap-2">
		<button class="action-button action-button--primary" on:click={() => void runSearch()}>Search</button>
		<button class="action-button action-button--secondary" on:click={() => (query = 'run')}>Run</button>
		<button class="action-button action-button--secondary" on:click={() => (query = 'ride')}>Ride</button>
	</div>

	{#if loading}
		<div class="mt-6 space-y-3">
			<div class="surface-panel animate-pulse min-h-24"></div>
			<div class="surface-panel animate-pulse min-h-24"></div>
		</div>
	{:else if error}
		<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
	{:else if results.length === 0}
		<div class="mt-6 section-block">
			<p class="label-sharp">No results yet</p>
			<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Type a query and run the search to populate this list.</p>
		</div>
	{:else}
		<div class="mt-6 grid gap-3">
			{#each results as result}
				<a class="section-block block transition hover:border-[var(--color-accent)]" href={`/diary/${result.strava_activity_id}`}>
					<div class="flex flex-wrap items-center justify-between gap-3">
						<p class="label-sharp">{result.type ?? 'Activity'}</p>
						<p class="text-xs text-[var(--color-text-muted)]">score {result.score ?? 0}</p>
					</div>
					<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{result.name ?? `Activity ${result.strava_activity_id}`}</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{new Date(result.start_date).toLocaleDateString('en-GB')}</p>
				</a>
			{/each}
		</div>
	{/if}

	<div class="mt-6 section-block">
		<p class="label-sharp">Search notes</p>
		<ul class="bullet-list mt-4">
			<li>Keyword search stays close to the stored text fields.</li>
			<li>Semantic search uses the same archive but changes the ranking path.</li>
			<li>Every result links straight into the activity detail page.</li>
		</ul>
	</div>
</section>