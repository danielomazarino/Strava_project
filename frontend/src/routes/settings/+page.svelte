<script lang="ts">
	import { browser } from '$app/environment';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { session } from '$lib/stores/session';
	import { theme } from '$lib/stores/theme';

	const shortcuts = [
		{ label: 'Dashboard', href: '/dashboard' },
		{ label: 'Insights', href: '/insights' },
		{ label: 'Ask Gemma', href: '/semantic-search' },
		{ label: 'Diary', href: '/diary' },
		{ label: 'Charts', href: '/charts' },
		{ label: 'Heatmap', href: '/heatmap' },
		{ label: 'Routes', href: '/routes' },
		{ label: 'Compare', href: '/compare' }
	];
</script>

<svelte:head>
	<title>Settings</title>
</svelte:head>

<PageShell title="Settings" subtitle="Theme and session controls live here.">
	<section class="surface-panel">
		<div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Preferences</p>
				<h2 class="section-title mt-2">Theme and session controls live here.</h2>
				<p class="section-subtitle">Use this page when you need to change appearance, clear the session, or move to the documentation surface.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => theme.toggleTheme()}>Toggle theme</button>
				<a class="action-button action-button--secondary" href="/about">About</a>
			</div>
		</div>

		<div class="mt-6 grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(280px,0.82fr)]">
			<div class="grid gap-4">
				<section class="surface-panel">
					<p class="label-sharp">Session and browser</p>
					<div class="mt-4 grid gap-4 text-sm leading-6 text-[var(--color-text-muted)]">
						<div>
							<p class="label-sharp">Session</p>
							{#if $session}
								<p class="mt-2">Athlete {$session.stravaAthleteId} · connected at {$session.connectedAt}</p>
								<div class="mt-3"><button class="action-button action-button--secondary" on:click={() => session.clearSession()}>Disconnect</button></div>
							{:else}
								<p class="mt-2">No active session. Use the sidebar system section to connect Strava again.</p>
							{/if}
						</div>
						<div>
							<p class="label-sharp">Theme</p>
							<p class="mt-2">Current theme: {$theme}</p>
						</div>
						<div>
							<p class="label-sharp">Browser state</p>
							<p class="mt-2">{browser ? 'Available.' : 'Server render only.'}</p>
						</div>
					</div>
				</section>

				<section class="surface-panel">
					<p class="label-sharp">Shortcuts</p>
					<div class="mt-4 flex flex-wrap gap-2">
						{#each shortcuts as shortcut}
							<a class="nav-pill nav-pill-secondary" href={shortcut.href}>{shortcut.label}</a>
						{/each}
					</div>
				</section>
			</div>

			<section class="surface-panel">
				<p class="label-sharp">Theme</p>
				<ul class="bullet-list mt-4">
					<li>Light mode keeps the product feeling open and editorial.</li>
					<li>Dark mode is available for low-light sessions.</li>
					<li>Theme persists in browser storage.</li>
				</ul>
			</section>
		</div>
	</section>
</PageShell>