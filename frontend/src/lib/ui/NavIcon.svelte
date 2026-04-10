<script lang="ts">
	export let name = 'dashboard';
</script>

<svg class="nav-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
	{#if name === 'dashboard'}
		<rect x="4" y="4" width="7" height="7" rx="1.5" />
		<rect x="13" y="4" width="7" height="7" rx="1.5" />
		<rect x="4" y="13" width="7" height="7" rx="1.5" />
		<rect x="13" y="13" width="7" height="7" rx="1.5" />
	{:else if name === 'insights'}
		<path d="M5 18.5V6.5" />
		<path d="M5 18.5H19" />
		<path d="M7 14.5L11 11.5L14.5 13.5L19 8.5" />
		<path d="M17.75 8.5H19V9.75" />
	{:else if name === 'ask'}
		<path d="M7 6.75H17a2.25 2.25 0 0 1 2.25 2.25v4a2.25 2.25 0 0 1-2.25 2.25H11.5L7 18.5v-3.25H7A2.25 2.25 0 0 1 4.75 13v-4A2.25 2.25 0 0 1 7 6.75Z" />
		<path d="M12 9.4l.6 1.5 1.5.6-1.5.6-.6 1.5-.6-1.5-1.5-.6 1.5-.6.6-1.5Z" />
	{:else if name === 'compare'}
		<path d="M6 5.5h5.5v13H6a1 1 0 0 1-1-1v-11a1 1 0 0 1 1-1Z" />
		<path d="M12.5 5.5H18a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1h-5.5v-13Z" />
		<path d="M10.5 9.25h3" />
		<path d="M10.5 14.75h3" />
	{:else if name === 'diary'}
		<path d="M7 5.5h9a2 2 0 0 1 2 2v11H8a1 1 0 0 1-1-1v-12Z" />
		<path d="M8.5 8h6" />
		<path d="M8.5 11h6" />
		<path d="M8.5 14h4" />
	{:else if name === 'charts'}
		<path d="M5 19.5h14" />
		<path d="M7.5 16v-4" />
		<path d="M11.5 16V7.5" />
		<path d="M15.5 16v-6.5" />
	{:else if name === 'heatmap'}
		<rect x="5" y="5" width="4.5" height="4.5" rx="1" />
		<rect x="10.75" y="5" width="4.5" height="4.5" rx="1" />
		<rect x="16.5" y="5" width="2.5" height="4.5" rx="1" />
		<rect x="5" y="10.75" width="4.5" height="4.5" rx="1" />
		<rect x="10.75" y="10.75" width="4.5" height="4.5" rx="1" />
		<rect x="16.5" y="10.75" width="2.5" height="4.5" rx="1" />
		<rect x="5" y="16.5" width="4.5" height="2.5" rx="1" />
		<rect x="10.75" y="16.5" width="4.5" height="2.5" rx="1" />
		<rect x="16.5" y="16.5" width="2.5" height="2.5" rx="1" />
	{:else if name === 'routes'}
		<path d="M6 17.5c3.25 0 3.25-11 7 0s3.75-2.5 5-2.5" />
		<circle cx="6" cy="17.5" r="1.4" />
		<circle cx="13" cy="7" r="1.4" />
		<circle cx="19" cy="15" r="1.4" />
	{:else if name === 'settings'}
		<circle cx="12" cy="12" r="3.2" />
		<path d="M12 4.5v2" />
		<path d="M12 17.5v2" />
		<path d="M4.5 12h2" />
		<path d="M17.5 12h2" />
		<path d="M6.2 6.2l1.4 1.4" />
		<path d="M16.4 16.4l1.4 1.4" />
		<path d="M17.8 6.2l-1.4 1.4" />
		<path d="M6.2 17.8l1.4-1.4" />
	{:else if name === 'auth'}
		<path d="M10 7H7.5A2.5 2.5 0 0 0 5 9.5v5A2.5 2.5 0 0 0 7.5 17H10" />
		<path d="M13.25 8.5 17 12l-3.75 3.5" />
		<path d="M17 12H10.5" />
	{:else if name === 'about'}
		<circle cx="12" cy="12" r="7.5" />
		<path d="M12 10.5v4.8" />
		<circle cx="12" cy="8.1" r="0.8" fill="currentColor" stroke="none" />
	{/if}
</svg>
