<script lang="ts">
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { keywordSearch, semanticSearch } from '$lib/api/search';
	import type { SearchResult } from '$lib/api/models';

	let query = 'Show me my best tempo runs with a hard finish and compare them with the easiest recovery days.';
	let mode: 'prompt' | 'exact' = 'prompt';
	let loading = false;
	let error = '';
	let results: SearchResult[] = [];
	let hasSearched = false;

	const examples = [
		'Show me the best tempo runs with a hard finish.',
		'Find the trail rides with the biggest climbing weeks.'
	];

	async function runSearch() {
		hasSearched = true;

		if (query.trim().length === 0) {
			results = [];
			error = 'Write a prompt before running an analysis.';
			return;
		}

		loading = true;
		error = '';
		try {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			results = mode === 'exact'
				? (await keywordSearch(athleteId, query)).results
				: (await semanticSearch(athleteId, query)).results;
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Search failed';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Ask Gemma</title>
</svelte:head>

<PageShell title="Ask Gemma" subtitle="Write longer prompts and let the local model analyze your training history.">
	<section class="surface-panel space-y-5">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Prompt studio</p>
				<h3 class="section-title mt-2">Ask for training patterns</h3>
				<p class="section-subtitle">Write one clear prompt. The UI stays compact so the prompt and result have a direct path.</p>
			</div>
			<div class="flex flex-wrap items-center gap-2">
				<select bind:value={mode} class="input-sharp">
					<option value="prompt">Gemma prompt</option>
					<option value="exact">Exact match</option>
				</select>
			</div>
		</div>

		<div class="grid gap-4">
			<div>
				<p class="label-sharp">Prompt</p>
				<textarea bind:value={query} class="input-sharp mt-3 min-h-[14rem] resize-y text-base leading-7" rows="8" placeholder="Describe the workout or training pattern you want to surface. For example: show me my tempo runs with a hard final split, then compare them with the easiest recovery days."></textarea>
			</div>

			<div>
				<p class="label-sharp">Examples</p>
				<div class="mt-3 flex flex-wrap gap-2">
					{#each examples as example}
						<button class="action-button action-button--secondary" on:click={() => (query = example)}>{example}</button>
					{/each}
				</div>
			</div>

			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void runSearch()}>Analyze</button>
				<p class="self-center text-sm text-[var(--color-text-muted)]">Results link into the diary detail pages.</p>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		<div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
			<div>
				<p class="label-sharp">Analysis</p>
				<h3 class="section-title mt-2">Matched activities</h3>
			</div>
			<p class="text-sm leading-6 text-[var(--color-text-muted)]">Prompt mode uses semantic analysis. Exact match is for known names, routes, or activity types.</p>
		</div>

		{#if loading}
			<div class="mt-6 space-y-3">
				{#each Array.from({ length: 3 })}
					<div class="surface-panel min-h-20 animate-pulse"></div>
				{/each}
			</div>
		{:else if error}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
		{:else if !hasSearched}
			<div class="mt-6 border border-dashed border-[var(--color-border)] bg-[var(--color-surface)] p-5 text-sm leading-6 text-[var(--color-text-muted)]">Gemma is ready for a longer prompt. Ask for a pattern, a comparison, or a summary of a specific training block, then press Analyze.</div>
		{:else if results.length === 0}
			<div class="mt-6 border border-dashed border-[var(--color-border)] bg-[var(--color-surface)] p-5 text-sm leading-6 text-[var(--color-text-muted)]">No matches yet. Try a more specific prompt or switch to exact match.</div>
		{:else}
			<div class="mt-6 space-y-3">
				{#each results as result}
					<a class="section-block block transition hover:border-[var(--color-accent)]" href={`/diary/${result.strava_activity_id}`}>
						<p class="label-sharp">{result.type ?? 'Activity'}</p>
						<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{result.name ?? `Activity ${result.strava_activity_id}`}</p>
						<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">score {result.score ?? 0} · {new Date(result.start_date).toLocaleDateString('en-GB')}</p>
					</a>
				{/each}
			</div>
		{/if}
	</section>
</PageShell>