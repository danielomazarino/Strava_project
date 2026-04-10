<script lang="ts">
	export let eyebrow = '';
	export let title = '';
	export let description = '';
	export let tone: 'neutral' | 'accent' = 'neutral';
	export let compact = false;

	let pinnedOpen = false;
	$: hasDetails = Boolean(description || $$slots.default);

	function togglePinnedOpen() {
		pinnedOpen = !pinnedOpen;
	}
</script>

<article
	class={`info-bubble group ${tone === 'accent' ? 'info-bubble--accent' : ''} ${compact ? 'info-bubble--compact' : ''} ${pinnedOpen ? 'is-open' : ''}`}
>
	<div class="info-bubble__header">
		<div class="min-w-0 flex-1">
			{#if eyebrow}
				<p class="label-sharp">{eyebrow}</p>
			{/if}

			{#if title}
				<h3 class="mt-2 text-xl font-semibold tracking-tight text-[var(--color-text)]">{title}</h3>
			{/if}
		</div>

		{#if hasDetails}
			<button
				type="button"
				class="info-bubble__trigger"
				aria-label={eyebrow ? `More information about ${eyebrow}` : 'More information'}
				aria-expanded={pinnedOpen}
				on:click={togglePinnedOpen}
			>
				i
			</button>
		{/if}
	</div>

	{#if hasDetails}
		<div class="info-bubble__panel" role="tooltip">
			{#if description}
				<p class="text-sm leading-6 text-[var(--color-text-muted)]">{description}</p>
			{/if}

			<slot />
		</div>
	{/if}
</article>
