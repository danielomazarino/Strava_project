<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { getSummaryInsight, getPatternInsight, compareRegions } from '$lib/api/insights';
	import type { PatternInsightResponse, SummaryInsightResponse, RegionComparisonResponse } from '$lib/api/insights';

	let loading = true;
	let error = '';
	let summary: SummaryInsightResponse | null = null;
	let patterns: PatternInsightResponse | null = null;
	let regionComparison: RegionComparisonResponse | null = null;
	let startDate = '';
	let endDate = '';
	let rangeDays = '30';
	let regionA = 'GB';
	let regionB = 'FR';
	const rangeOptions = [
		{ label: '7 days', value: 7 },
		{ label: '30 days', value: 30 },
		{ label: '90 days', value: 90 }
	];

	function defaultRange(daysBack: number) {
		rangeDays = String(daysBack);
		const now = new Date();
		const start = new Date(now);
		start.setDate(start.getDate() - daysBack);
		startDate = start.toISOString().slice(0, 10);
		endDate = now.toISOString().slice(0, 10);
	}

	function setRange(daysBack: string) {
		defaultRange(Number(daysBack));
		void loadInsights();
	}

	async function loadInsights() {
		loading = true;
		error = '';
		try {
			const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
			const start = new Date(`${startDate}T00:00:00Z`);
			const end = new Date(`${endDate}T23:59:59Z`);
			summary = await getSummaryInsight(athleteId, start, end);
			patterns = await getPatternInsight(athleteId, start, end);
			regionComparison = await compareRegions(athleteId, regionA, regionB, start, end);
		} catch (caught) {
			error = caught instanceof Error ? caught.message : 'Unable to load insights';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		defaultRange(30);
		void loadInsights();
	});
</script>

<svelte:head>
	<title>Insights</title>
</svelte:head>

<PageShell title="Insights" subtitle="Summary, patterns, and region comparisons in one place.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Analysis window</p>
				<h2 class="section-title mt-2">Summary, patterns, and region comparisons in one place.</h2>
				<p class="section-subtitle">Choose a window first, then ask the model to summarize the last few weeks or compare regions with the same range.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void loadInsights()}>Refresh</button>
				<select class="input-sharp" bind:value={rangeDays} on:change={(event) => setRange((event.currentTarget as HTMLSelectElement).value)}>
					{#each rangeOptions as option}
						<option value={option.value}>{option.label}</option>
					{/each}
				</select>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		<div class="grid gap-4 md:grid-cols-3">
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Start date</span>
				<input bind:value={startDate} type="date" class="input-sharp" />
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">End date</span>
				<input bind:value={endDate} type="date" class="input-sharp" />
			</label>
			<div class="flex items-end">
				<button class="action-button action-button--primary w-full" on:click={() => void loadInsights()}>Load insights</button>
			</div>
		</div>

		{#if loading}
			<div class="mt-6 grid gap-4 md:grid-cols-3">
				<div class="surface-panel min-h-44 animate-pulse"></div>
				<div class="surface-panel min-h-44 animate-pulse"></div>
				<div class="surface-panel min-h-44 animate-pulse"></div>
			</div>
		{:else if error}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
		{:else if summary && patterns && regionComparison}
			<div class="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)]">
				<div class="grid gap-4">
					<div class="section-block border-[rgba(252,76,2,0.24)] bg-[rgba(252,76,2,0.06)]">
						<p class="label-sharp">Training story</p>
						<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{summary.analysis.summary}</p>
						<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{summary.analysis.volume ?? 'Volume unknown'}</p>
					</div>
					<div class="grid gap-4 sm:grid-cols-2">
						<div class="section-block">
							<p class="label-sharp">Volume</p>
							<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{summary.analysis.volume ?? 'n/a'}</p>
						</div>
						<div class="section-block">
							<p class="label-sharp">Region comparison</p>
							<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{regionComparison.analysis.region_a} vs {regionComparison.analysis.region_b}</p>
							<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{regionComparison.analysis.perceived_effort}</p>
						</div>
					</div>
					<div class="section-block">
						<p class="label-sharp">Pattern signals</p>
						<div class="mt-4 grid gap-3 sm:grid-cols-2">
							<div>
								<p class="label-sharp">Fatigue</p>
								<ul class="bullet-list mt-3">{#each patterns.analysis.fatigue ?? [] as item}<li>{item}</li>{/each}</ul>
							</div>
							<div>
								<p class="label-sharp">Terrain</p>
								<ul class="bullet-list mt-3">{#each patterns.analysis.terrain_effects ?? [] as item}<li>{item}</li>{/each}</ul>
							</div>
						</div>
					</div>
				</div>

				<div class="grid gap-4">
					<div class="section-block">
						<p class="label-sharp">Signals</p>
						<ul class="bullet-list mt-4">
							<li>Fatigue and terrain are the first things to scan.</li>
							<li>Motivation and weather are still part of the model output, but they stay secondary.</li>
							<li>Region comparison answers whether one area feels harder or faster than another.</li>
						</ul>
					</div>
					<div class="section-block">
						<p class="label-sharp">Region differences</p>
						<ul class="bullet-list mt-4">
							{#each regionComparison.analysis.terrain_differences ?? [] as item}<li>{item}</li>{/each}
							{#each regionComparison.analysis.pacing_differences ?? [] as item}<li>{item}</li>{/each}
						</ul>
					</div>
				</div>
			</div>
		{/if}
	</section>
</PageShell>