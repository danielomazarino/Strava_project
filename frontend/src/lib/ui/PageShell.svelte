<script lang="ts">
	const hasAside = Boolean($$slots.aside);
</script>

<section class="page-shell">
	<div class={`page-shell__grid ${hasAside ? '' : 'page-shell__grid--single'}`}>
		<div class="page-shell__main">
			<slot />
		</div>
		{#if hasAside}
			<aside class="page-shell__aside">
				<slot name="aside" />
			</aside>
		{/if}
	</div>
</section>
