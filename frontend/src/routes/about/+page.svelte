<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { getAdminOverview, type AdminOverviewResponse } from '$lib/api/admin';
	import { getSessionDisplayName, session } from '$lib/stores/session';
	import AdminRecordExplorer from '$lib/components/AdminRecordExplorer.svelte';

	const docs = [
		{ title: 'Architecture', text: 'App structure, route responsibilities, and shared patterns.' },
		{ title: 'Data model', text: 'The activity, diary, and insight shapes used by the UI.' },
		{ title: 'Testing', text: 'Validation commands and coverage strategy for the build.' },
		{ title: 'Deployment', text: 'Release checklist, environment details, and runbook notes.' }
	];

	const overviewStats = [
		{ label: 'Users', value: () => overview?.totals.users ?? '0', detail: 'Imported Strava accounts' },
		{ label: 'Activities', value: () => overview?.totals.activities ?? '0', detail: 'Rows available for diary and detail views' },
		{ label: 'Active tokens', value: () => overview?.totals.active_tokens ?? '0', detail: 'Refreshable sessions' },
		{ label: 'Expired', value: () => overview?.totals.expired_tokens ?? '0', detail: 'Sessions that need a refresh' }
	];

	const formatDate = new Intl.DateTimeFormat('en-GB', {
		weekday: 'short',
		day: '2-digit',
		month: 'short',
		year: 'numeric'
	});

	const formatTime = new Intl.DateTimeFormat('en-GB', {
		hour: '2-digit',
		minute: '2-digit'
	});

	let loading = true;
	let error = '';
	let overview: AdminOverviewResponse | null = null;
	let overviewUnavailable = false;

	function formatDuration(minutes: number | null): string {
		if (minutes == null) {
			return 'n/a';
		}

		return `${Math.round(minutes / 60)}h ${Math.round(minutes % 60)}m`;
	}

	onMount(async () => {
		try {
			overview = await getAdminOverview();
		} catch (caught) {
			const message = caught instanceof Error ? caught.message : 'Unable to load admin overview';
			if (message.includes('Not found')) {
				overviewUnavailable = true;
				return;
			}

			error = message;
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>About / documentation</title>
</svelte:head>

<PageShell title="About / documentation" subtitle="Admin summary, login explanation, and reference material live here.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Admin surface</p>
				<h2 class="section-title mt-2">Read-only data browser and product notes.</h2>
				<p class="section-subtitle">This page explains login, explicit demo sessions, and the local data browser without introducing an editable admin workflow.</p>
			</div>
			<div class="flex flex-wrap gap-4 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--color-text-muted)]">
				<a class="transition-colors hover:text-[var(--color-text)]" href="/settings">Open settings</a>
				<a class="transition-colors hover:text-[var(--color-text)]" href="/diary">Open diary</a>
			</div>
		</div>
	</section>

	<section class="surface-panel">
		<p class="label-sharp">Imported data summary</p>
		<h3 class="section-title mt-2">Read-only admin overview</h3>
		<p class="section-subtitle">This is the local backend record browser. It shows the current dev database state, not a fake preview.</p>
		{#if overviewUnavailable}
			<div class="mt-6 border border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] p-4 text-sm leading-6 text-[var(--color-text-muted)]">
				The read-only overview is only available in local development. Production keeps this section documentation-only until dedicated admin authentication is added.
			</div>
		{:else}
			{#if loading}
				<div class="mt-6 grid gap-4 md:grid-cols-4">
					<div class="surface-panel min-h-24 animate-pulse"></div>
					<div class="surface-panel min-h-24 animate-pulse"></div>
					<div class="surface-panel min-h-24 animate-pulse"></div>
					<div class="surface-panel min-h-24 animate-pulse"></div>
				</div>
			{:else if error}
				<div class="mt-6 border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
			{:else if overview}
				<div class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
					{#each overviewStats as stat}
						<div>
							<p class="label-sharp">{stat.label}</p>
							<p class="mt-2 text-3xl font-semibold tracking-tight text-[var(--color-text)]">{stat.value()}</p>
							<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{stat.detail}</p>
						</div>
					{/each}
				</div>
				<div class="mt-6 overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface)]">
					<table class="min-w-full text-left text-sm">
						<thead class="border-b border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] text-xs uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
							<tr>
								<th class="px-4 py-3">Athlete</th>
								<th class="px-4 py-3">Activities</th>
								<th class="px-4 py-3">Token</th>
								<th class="px-4 py-3">Latest activity</th>
							</tr>
						</thead>
						<tbody>
							{#each overview.users as user}
								<tr class="border-b border-[var(--color-border)] last:border-b-0">
									<td class="px-4 py-3 font-medium text-[var(--color-text)]">{user.strava_athlete_id}</td>
									<td class="px-4 py-3 text-[var(--color-text-muted)]">{user.activity_count}</td>
									<td class="px-4 py-3 text-[var(--color-text-muted)]">{user.token_health} · expires {formatDate.format(new Date(user.token_expires_at))}</td>
									<td class="px-4 py-3 text-[var(--color-text-muted)]">{user.latest_activity_name ?? 'No activities yet'}{#if user.latest_activity_start_date} · {formatDate.format(new Date(user.latest_activity_start_date))}{/if}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				<div class="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(320px,0.75fr)]">
					<div class="surface-panel p-0">
						<AdminRecordExplorer records={overview.records} />
					</div>
					<div class="surface-panel">
						<p class="label-sharp">Reference notes</p>
						<div class="mt-4 space-y-4">
							{#each docs as doc}
								<div>
									<p class="label-sharp">{doc.title}</p>
									<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{doc.text}</p>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{/if}
		{/if}
	</section>

	<svelte:fragment slot="aside">
		<div class="grid gap-6">
			<section class="surface-panel">
				<p class="label-sharp">Reference docs</p>
				<div class="mt-4 space-y-4">
					{#each docs as doc}
						<div>
							<p class="label-sharp">{doc.title}</p>
							<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{doc.text}</p>
						</div>
					{/each}
				</div>
			</section>
		</div>
	</svelte:fragment>
</PageShell>