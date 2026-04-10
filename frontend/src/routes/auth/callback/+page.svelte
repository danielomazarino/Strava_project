<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { completeOAuthCallback } from '$lib/api/auth';
	import { session } from '$lib/stores/session';

	let message = 'Connecting to the Strava backend...';
	let errorMessage = '';

	onMount(async () => {
		const currentUrl = new URL(window.location.href);
		const redirectedUserId = currentUrl.searchParams.get('user_id');
		const redirectedAthleteId = currentUrl.searchParams.get('strava_athlete_id');

		if (redirectedUserId && redirectedAthleteId) {
			session.setSession({
				status: 'connected',
				userId: redirectedUserId,
				stravaAthleteId: Number(redirectedAthleteId),
				connectedAt: new Date().toISOString()
			});
			message = 'Connected. Sending you back to the diary.';
			await goto('/diary');
			return;
		}

		const code = currentUrl.searchParams.get('code');
		const state = currentUrl.searchParams.get('state');

		if (!code || !state) {
			errorMessage = 'Missing OAuth callback parameters.';
			message = 'Unable to complete the handoff.';
			return;
		}

		try {
			const connectedUser = await completeOAuthCallback(code, state);
			session.setSession({
				status: 'connected',
				userId: connectedUser.user_id,
				stravaAthleteId: connectedUser.strava_athlete_id,
				connectedAt: new Date().toISOString()
			});
			message = 'Connected. Sending you back to the diary.';
			await goto('/diary');
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Unknown callback error';
			message = 'The backend rejected the callback.';
		}
	});
</script>

<svelte:head>
	<title>Connecting Strava</title>
</svelte:head>

<section class="surface-panel mx-auto max-w-3xl overflow-hidden">
	<div class="grid gap-0 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
		<div class="bg-[linear-gradient(135deg,rgba(22,19,17,0.98),rgba(42,34,28,0.95)_55%,rgba(22,19,17,0.98))] p-7 text-paper md:p-10">
			<p class="kicker text-paper/70">OAuth callback</p>
			<h1 class="mt-3 font-display text-5xl leading-tight text-paper">Finishing connection</h1>
			<p class="mt-4 text-base leading-8 text-paper/80">{message}</p>
		</div>

		<div class="p-7 md:p-10">
			{#if errorMessage}
				<div class="section-block border-[rgba(252,76,2,0.24)] bg-[rgba(252,76,2,0.06)]">
					<p class="label-sharp">OAuth error</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">{errorMessage}</p>
				</div>
			{:else}
				<div class="section-block border-[rgba(252,76,2,0.24)] bg-[rgba(252,76,2,0.06)]">
					<p class="label-sharp">Session handoff</p>
					<p class="mt-2 text-xl font-semibold tracking-tight text-[var(--color-text)]">In progress</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Storing the session locally and returning to the app shell.</p>
				</div>
			{/if}
		</div>
	</div>
</section>