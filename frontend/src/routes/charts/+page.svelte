<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { listDiaryEntries } from '$lib/api/diary';
	import type { DiaryEntry } from '$lib/api/models';
	import { formatPace, groupByMonth, groupByWeek, paceBuckets, summarizeTrends } from '$lib/utils/training';

	type ViewMode = 'weekly' | 'monthly' | 'pace';

	let loading = true;
	let loadError = '';
	let entries: DiaryEntry[] = [];
	let viewMode: ViewMode = 'weekly';

	const formatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

	onMount(async () => {
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;

		try {
			const response = await listDiaryEntries(athleteId);
			entries = response.entries;
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'Unable to load chart data';
		} finally {
			loading = false;
		}
	});

	$: trends = summarizeTrends(entries);
	$: weeklyBuckets = groupByWeek(entries).slice(-8);
	$: monthlyBuckets = groupByMonth(entries).slice(-8);
	$: paceDistribution = paceBuckets(entries);
	$: highestWeekly = Math.max(...weeklyBuckets.map((bucket) => bucket.distance), 1);
	$: highestMonthly = Math.max(...monthlyBuckets.map((bucket) => bucket.distance), 1);
</script>

<svelte:head>
	<title>Charts</title>
</svelte:head>

<PageShell title="Charts" subtitle="Weekly volume, monthly volume, and pace distribution.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Trend views</p>
				<h2 class="section-title mt-2">See the weekly and monthly shape of training.</h2>
				<p class="section-subtitle">Use this page to check whether the archive is trending up, steady, or tapering.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<select class="input-sharp min-w-[13rem]" bind:value={viewMode}>
					<option value="weekly">Weekly volume</option>
					<option value="monthly">Monthly volume</option>
					<option value="pace">Pace distribution</option>
				</select>
				<a class="action-button action-button--primary" href="/dashboard">Back to dashboard</a>
				<button class="action-button action-button--secondary" on:click={() => location.reload()}>Reload data</button>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		{#if loading}
			<div class="surface-panel min-h-72 animate-pulse"></div>
		{:else if loadError}
			<div class="border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{loadError}</div>
		{:else}
				<div class="section-block">
					<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
						<div>
							<p class="label-sharp">At a glance</p>
							<div class="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
								<div>
									<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Activities</p>
									<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{String(trends.activityCount)}</p>
								</div>
								<div>
									<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Distance</p>
									<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{formatter.format(trends.totalDistance / 1000)} km</p>
								</div>
								<div>
									<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Active days</p>
									<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{String(trends.activeDays)}</p>
								</div>
								<div>
									<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Longest streak</p>
									<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{trends.longestStreak} days</p>
								</div>
							</div>
						</div>
						<p class="text-sm leading-6 text-[var(--color-text-muted)]">Switch the selector above to focus on one chart at a time instead of stacking three dense panels.</p>
					</div>

					<div class="mt-6 border border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] p-4">
						{#if viewMode === 'weekly'}
							<p class="label-sharp">Weekly volume</p>
							<div class="mt-6 flex h-56 items-end gap-3">
								{#each weeklyBuckets as bucket}
									<div class="flex flex-1 flex-col items-center gap-2">
										<div class="flex w-full items-end justify-center border border-[var(--color-border)] bg-[rgba(252,76,2,0.08)]" style={`height:${Math.max((bucket.distance / highestWeekly) * 180, 10)}px`}>
											<div class="h-full w-full bg-[var(--color-accent)]"></div>
										</div>
										<p class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--color-text-muted)]">{bucket.label.slice(5)}</p>
										<p class="text-xs text-[var(--color-text-muted)]">{formatter.format(bucket.distance / 1000)} km</p>
									</div>
								{/each}
							</div>
						{:else if viewMode === 'monthly'}
							<p class="label-sharp">Monthly volume</p>
							<div class="mt-6 flex h-56 items-end gap-3">
								{#each monthlyBuckets as bucket}
									<div class="flex flex-1 flex-col items-center gap-2">
										<div class="flex w-full items-end justify-center border border-[var(--color-border)] bg-[rgba(252,76,2,0.08)]" style={`height:${Math.max((bucket.distance / highestMonthly) * 180, 10)}px`}>
											<div class="h-full w-full bg-[var(--color-accent)]"></div>
										</div>
										<p class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--color-text-muted)]">{bucket.label}</p>
										<p class="text-xs text-[var(--color-text-muted)]">{formatter.format(bucket.distance / 1000)} km</p>
									</div>
								{/each}
							</div>
						{:else}
							<p class="label-sharp">Pace distribution</p>
							<p class="mt-2 text-sm text-[var(--color-text-muted)]">Average pace: {formatPace(trends.averagePace)}</p>
							<div class="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
								{#each paceDistribution as bucket}
									<div class="section-block">
										<p class="label-sharp">{bucket.label}</p>
										<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{String(bucket.count)}</p>
									</div>
								{/each}
							</div>
						{/if}
					</div>

					<ul class="bullet-list mt-6">
						<li>Use the mode selector to keep one analysis frame visible at a time.</li>
						<li>The summary metrics stay fixed so you can compare the chart against the archive shape.</li>
					</ul>
				</div>
		{/if}
	</section>
</PageShell>