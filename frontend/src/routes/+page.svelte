<script lang="ts">
	import { getSessionDisplayName, session } from '$lib/stores/session';
</script>

<section class="surface-panel">
	<div class="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
		<div>
			<p class="label-sharp">Overview</p>
			<h1 class="section-title mt-2">Your Strava training archive.</h1>
			<p class="section-subtitle">Diary, analysis, maps, and AI insights in one compact workspace.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<a class="action-button action-button--primary" href="/diary">Open diary</a>
			<a class="action-button action-button--secondary" href="/dashboard">Dashboard</a>
		</div>
	</div>

	<div class="mt-6 section-block">
		{#if $session}
			<p class="label-sharp">Session</p>
			<p class="mt-2 text-lg font-semibold tracking-tight text-[var(--color-text)]">{getSessionDisplayName($session)}</p>
			<p class="mt-1 text-sm leading-6 text-[var(--color-text-muted)]">Connected at {$session.connectedAt}</p>
		{:else}
			<p class="label-sharp">Not connected</p>
			<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Use the sidebar to connect Strava and start exploring your training history.</p>
			<div class="mt-3"><a class="action-button action-button--primary" href="/auth/login">Connect Strava</a></div>
		{/if}
	</div>
</section>