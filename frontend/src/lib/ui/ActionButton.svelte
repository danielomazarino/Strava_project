<script lang="ts">
	export let href: string | null = null;
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let variant: 'primary' | 'secondary' | 'text' = 'secondary';
	export let disabled = false;
</script>

{#if href}
	<a class={`action-button action-button--${variant}`} href={href} aria-disabled={disabled}>{#if $$slots.default}<slot />{/if}</a>
{:else}
	<button class={`action-button action-button--${variant}`} type={type} disabled={disabled}>
		<slot />
	</button>
{/if}
