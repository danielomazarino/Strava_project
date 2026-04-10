<script lang="ts">
	import NavIcon from './NavIcon.svelte';

	export let href = '#';
	export let label = '';
	export let icon = 'dashboard';
	export let active = false;
	export let variant: 'primary' | 'secondary' | undefined = undefined;
	export let tone: 'primary' | 'secondary' | undefined = undefined;
	let resolvedVariant: 'primary' | 'secondary' = 'secondary';

	$: resolvedVariant = variant ?? tone ?? 'secondary';
</script>

<a
	class={`nav-link nav-link--${resolvedVariant} ${active ? 'is-active' : ''}`}
	href={href}
	aria-current={active ? 'page' : undefined}
	aria-label={label}
>
	<span class="nav-link__icon" aria-hidden="true">
		<NavIcon name={icon} />
	</span>
	<span class="nav-link__label">{label}</span>
</a>
