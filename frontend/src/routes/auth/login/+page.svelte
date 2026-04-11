<script lang="ts">
	import { goto } from '$app/navigation';
	import { createDemoSession, session } from '$lib/stores/session';

	export let data: {
		apiBaseConfigured: boolean;
		mockAuthEnabled: boolean;
		demoSessionAvailable: boolean;
	};

	function openDashboard() {
		void goto('/dashboard');
	}

	function startDemoSession() {
		session.setSession(createDemoSession());
		void goto('/dashboard');
	}
</script>

<svelte:head>
	<title>Sign in</title>
</svelte:head>

<section class="mx-auto max-w-4xl overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface)]">
	<div class="grid gap-0 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
		<div class="bg-[linear-gradient(135deg,rgba(22,19,17,0.98),rgba(39,33,28,0.96)_52%,rgba(22,19,17,0.98))] p-7 text-paper md:p-10">
			<p class="label-sharp text-paper/70">Authentication</p>
			<h1 class="mt-3 text-4xl font-semibold tracking-tight text-paper md:text-6xl">Sign in</h1>
			<p class="mt-4 max-w-xl text-base leading-8 text-paper/80">
				You can connect to Strava through the backend or start a local demo session and explore the app immediately.
			</p>
			<div class="mt-8 grid gap-3 text-sm leading-6 text-paper/75">
				<p>Connect through the backend when the Strava auth flow is available.</p>
				<p>Use the demo session if you only want to inspect the UI and data browser.</p>
			</div>
		</div>

		<div class="p-7 md:p-10">
			<div class="surface-panel">
				<p class="label-sharp">Current state</p>
				<div class="mt-4 grid gap-3 text-sm leading-6 text-[var(--color-text-muted)]">
					<p>{data.apiBaseConfigured ? 'The API base is configured, but the login URL resolves back to this frontend. Check the proxy or backend host settings.' : 'No backend API base URL is configured in the frontend environment.'}</p>
					<p>{data.mockAuthEnabled ? 'Mock auth is enabled in development, but it still depends on a backend URL unless you wire a local-only demo session.' : 'Development mock auth is disabled.'}</p>
				</div>

				<div class="mt-6 flex flex-wrap gap-2">
					{#if data.demoSessionAvailable}
						<button class="action-button action-button--primary" type="button" on:click={startDemoSession}>Start demo session</button>
					{/if}
					<button class="action-button action-button--secondary" type="button" on:click={openDashboard}>Skip for now</button>
					<a class="action-button action-button--secondary" href="/settings">Open settings</a>
				</div>
			</div>

			<div class="section-block mt-6">
				<p class="label-sharp">Demo mode</p>
				<ul class="bullet-list mt-4">
					{#if data.demoSessionAvailable}
						<li>Start demo session creates a local session and loads built-in sample data.</li>
					{:else}
						<li>Demo session is only available in local development.</li>
					{/if}
					<li>Skip for now keeps the shell open if you only want to inspect layout.</li>
					<li>Set PUBLIC_API_BASE_URL to /api and BACKEND_API_BASE_URL on the server before sharing the app.</li>
				</ul>
			</div>
		</div>
	</div>
</section>