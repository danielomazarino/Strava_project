<script lang="ts">
	import { browser } from '$app/environment';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { getSessionDisplayName, session } from '$lib/stores/session';
	import { theme } from '$lib/stores/theme';
</script>

<svelte:head>
	<title>Settings</title>
</svelte:head>

<PageShell title="Settings" subtitle="Session and appearance controls.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Preferences</p>
				<h2 class="section-title mt-2">Session and appearance controls.</h2>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => theme.toggleTheme()}>Toggle theme</button>
				<a class="action-button action-button--secondary" href="/about">About</a>
			</div>
		</div>

		<div class="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(280px,0.7fr)]">
			<section class="surface-panel">
				<p class="label-sharp">Session</p>
				<div class="mt-4 grid gap-4 text-sm leading-6 text-[var(--color-text-muted)]">
					{#if $session}
						<div>
							<p class="mt-2 font-semibold text-[var(--color-text)]">{getSessionDisplayName($session)}</p>
							<p class="mt-1">Connected at {$session.connectedAt}</p>
						</div>
						<div class="flex flex-wrap gap-2">
							<button class="action-button action-button--secondary" on:click={() => session.clearSession()}>Sign out</button>
						</div>
						<p class="text-xs leading-5">Sign out clears the local session. Your Strava data stays in the app database. Connect again via the sidebar to resume.</p>
					{:else}
						<p>Not connected.</p>
						<a class="action-button action-button--primary w-fit" href="/auth/login">Connect Strava</a>
					{/if}
				</div>
			</section>

			<section class="surface-panel">
				<p class="label-sharp">Appearance</p>
				<div class="mt-4 grid gap-3 text-sm leading-6 text-[var(--color-text-muted)]">
					<p>Current theme: {$theme}</p>
					{#if browser}
						<p>Browser storage: available.</p>
					{/if}
				</div>
			</section>
		</div>
	</section>
</PageShell>