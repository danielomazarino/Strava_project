<script lang="ts">
	import { theme } from '$lib/stores/theme';
	import { onMount } from 'svelte';

	let hydrated = false;

	onMount(() => {
		hydrated = true;
	});
</script>

<button class="nav-pill nav-pill-accent min-w-[8.5rem] justify-center" type="button" on:click={() => theme.toggleTheme()}>
	{#if $theme === 'dark'}
		{hydrated ? 'Light mode' : 'Dark mode'}
	{:else}
		{hydrated ? 'Dark mode' : 'Light mode'}
	{/if}
</button>