<script lang="ts">
	export let href = '#';
	export let label = '';
	export let active = false;
	export let tone: 'primary' | 'secondary' = 'secondary';
</script>

<a
	class={`nav-pill ${tone === 'primary' ? 'nav-pill-primary' : 'nav-pill-secondary'} ${active ? 'nav-pill-active' : ''}`}
	href={href}
>
	{label}
</a>