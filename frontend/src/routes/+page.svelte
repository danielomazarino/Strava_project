<script lang="ts">
	import { session } from '$lib/stores/session';

	const highlights = [
		{ label: 'Imported activities', value: '3,938' },
		{ label: 'Oldest entry', value: '2013' },
		{ label: 'Prompt hits', value: '2,856' }
	];

	const sections = [
		{
			id: 'diary',
			title: 'Diary',
			text: 'Browse the full activity stream with search, type filters, and deep links into route detail.'
		},
		{
			id: 'search',
			title: 'Ask Gemma',
			text: 'Long-form prompts and exact lookup sit on one surface, so analysis stays close to the data.'
		},
		{
			id: 'dashboard',
			title: 'Dashboard',
			text: 'Weekly summaries, charts, and quick stats for the first glance at training trends.'
		},
		{
			id: 'about',
			title: 'System',
			text: 'Settings, Strava connection, and documentation live in the system section.'
		}
	];
</script>

<section class="surface-panel">
	<div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
		<div>
			<p class="label-sharp">Overview</p>
			<h1 class="section-title mt-2">A local training archive with one clear shell.</h1>
			<p class="section-subtitle">Diary, search, charts, and system tools all share the same compact workspace.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<a class="action-button action-button--primary" href="/diary">Open diary</a>
			<a class="action-button action-button--secondary" href="/dashboard">Open dashboard</a>
		</div>
	</div>

	<div class="mt-6 grid gap-3 sm:grid-cols-3">
		{#each highlights as highlight}
			<div class="section-block">
				<p class="label-sharp">{highlight.label}</p>
				<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{highlight.value}</p>
			</div>
		{/each}
	</div>
</section>

<section class="mt-6 grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
	<div class="surface-panel">
		<p class="label-sharp">Session</p>
		<div class="mt-4 section-block">
			{#if $session}
				<p class="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Connected athlete</p>
				<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{$session.stravaAthleteId}</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">User id {$session.userId} · connected at {$session.connectedAt}</p>
			{:else}
				<p class="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">No saved session</p>
				<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Open the system section in the sidebar to connect Strava or review system controls.</p>
			{/if}
		</div>
	</div>

	<div class="surface-panel">
		<p class="label-sharp">Navigation</p>
		<div class="mt-4 flex flex-wrap gap-2">
			{#each sections as section}
				<a class="action-button action-button--secondary" href={`/${section.id}`}>{section.title}</a>
			{/each}
		</div>
		<div class="mt-6 section-block">
			<p class="label-sharp">Interface notes</p>
			<ul class="bullet-list mt-4">
				<li>The shell uses the same spacing and control size everywhere.</li>
				<li>Pages should stay readable on laptop and mobile widths.</li>
				<li>Dense stacks get merged before any new visual decoration is added.</li>
			</ul>
		</div>
	</div>
</section>