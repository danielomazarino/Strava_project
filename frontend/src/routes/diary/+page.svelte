<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { listDiaryEntries } from '$lib/api/diary';
	import type { DiaryEntry } from '$lib/api/models';

	const PAGE_SIZE = 12;

	let loading = true;
	let loadError = '';
	let diaryEntries: DiaryEntry[] = [];
	let searchQuery = '';
	let selectedType = 'all';
	let visibleCount = PAGE_SIZE;

	const formatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

	function resetPagination() {
		visibleCount = PAGE_SIZE;
	}

	function formatDateLabel(value: string): string {
		return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));
	}

	const loadDiary = async () => {
		loading = true;
		loadError = '';
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;

		try {
			const response = await listDiaryEntries(athleteId);
			diaryEntries = response.entries;
			resetPagination();
		} catch (caught) {
			loadError = caught instanceof Error ? caught.message : 'Unable to load diary entries';
		} finally {
			loading = false;
		}
	};

	onMount(() => {
		void loadDiary();
	});

	$: uniqueTypes = Array.from(new Set(diaryEntries.map((entry) => entry.type).filter(Boolean) as string[]));
	$: filteredEntries = diaryEntries.filter((entry) => {
		const query = searchQuery.trim().toLowerCase();
		const matchesType = selectedType === 'all' || entry.type === selectedType;
		const matchesQuery =
			query.length === 0 ||
			[entry.name, entry.type, entry.description, entry.location_country].filter(Boolean).some((value) => String(value).toLowerCase().includes(query));
		return matchesType && matchesQuery;
	});
	$: visibleEntries = filteredEntries.slice(0, visibleCount);
	$: totalDistance = filteredEntries.reduce((sum, entry) => sum + (entry.distance ?? 0), 0);
	$: dateRange = filteredEntries.length
		? `${formatDateLabel(filteredEntries[filteredEntries.length - 1].start_date)} to ${formatDateLabel(filteredEntries[0].start_date)}`
		: 'No entries yet';
	$: if (visibleCount > filteredEntries.length) {
		visibleCount = filteredEntries.length;
	}
</script>

<svelte:head>
	<title>Diary</title>
</svelte:head>

<PageShell title="Diary" subtitle="Browse the backfilled Strava history.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">History browser</p>
				<h2 class="section-title mt-2">Browse the backfilled activity archive.</h2>
				<p class="section-subtitle">Search by name, type, country, or notes. Use the type filter when you want a narrower list.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void loadDiary()}>Reload diary</button>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		<div class="grid gap-4 sm:grid-cols-3">
			<div class="section-block">
				<p class="label-sharp">Activities</p>
				<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{String(filteredEntries.length)}</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Matching entries in the current filter</p>
			</div>
			<div class="section-block">
				<p class="label-sharp">Distance</p>
				<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{(totalDistance / 1000).toFixed(1)} km</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Total distance across the filtered archive</p>
			</div>
			<div class="section-block">
				<p class="label-sharp">Range</p>
				<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{dateRange}</p>
			</div>
		</div>

		<div class="mt-6 grid gap-3 md:grid-cols-[minmax(0,1fr)_220px]">
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Search</span>
				<input bind:value={searchQuery} on:input={resetPagination} class="input-sharp" placeholder="Search by name, type, country, or notes" />
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Type</span>
				<select bind:value={selectedType} on:change={resetPagination} class="input-sharp">
					<option value="all">All types</option>
					{#each uniqueTypes as type}
						<option value={type}>{type}</option>
					{/each}
				</select>
			</label>
		</div>

		{#if loading}
			<div class="mt-6 space-y-3">
				<div class="surface-panel animate-pulse min-h-24"></div>
				<div class="surface-panel animate-pulse min-h-24"></div>
				<div class="surface-panel animate-pulse min-h-24"></div>
			</div>
		{:else if loadError}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{loadError}</div>
		{:else if filteredEntries.length === 0}
			<div class="mt-6 section-block">
				<p class="section-title">No matching activities</p>
				<ul class="bullet-list mt-4">
					<li>Try a shorter search term or clear the type filter.</li>
					<li>Switch back to all activity types if you want the full archive again.</li>
				</ul>
			</div>
		{:else}
			<div class="mt-6 grid gap-3">
				{#each visibleEntries as entry}
					<a class="section-block block transition hover:border-[var(--color-accent)]" href={`/diary/${entry.strava_activity_id}`}>
						<div class="flex flex-wrap items-center justify-between gap-3">
							<p class="label-sharp">{entry.type ?? 'Activity'}</p>
							<p class="text-xs text-[var(--color-text-muted)]">{formatDateLabel(entry.start_date)}</p>
						</div>
						<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{entry.name ?? `Activity ${entry.strava_activity_id}`}</p>
						<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{formatter.format((entry.distance ?? 0) / 1000)} km · {Math.round((entry.moving_time ?? 0) / 60)} min</p>
					</a>
				{/each}
			</div>

			{#if visibleCount < filteredEntries.length}
				<div class="mt-6">
					<button class="action-button action-button--secondary" on:click={() => (visibleCount = Math.min(visibleCount + PAGE_SIZE, filteredEntries.length))}>Load more</button>
				</div>
			{/if}
		{/if}
	</section>
</PageShell>