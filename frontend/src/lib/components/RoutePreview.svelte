<script lang="ts">
	import { buildPolylinePreview, decodePolyline } from '$lib/geo/polyline';

	export let polyline: string | null = null;

	$: points = polyline ? decodePolyline(polyline) : [];
	$: preview = buildPolylinePreview(points);
</script>

{#if preview}
	<div class="overflow-hidden rounded-[2rem] border border-white/20 bg-[linear-gradient(180deg,rgba(20,18,15,0.98),rgba(28,24,20,0.96))] p-4 shadow-soft">
		<div class="mb-3 flex items-center justify-between text-xs uppercase tracking-[0.24em] text-paper/65">
			<span>Route preview</span>
			<span>{preview.points.length} points</span>
		</div>
		<svg viewBox={`0 0 ${preview.width} ${preview.height}`} class="h-auto w-full rounded-[1.5rem] bg-[radial-gradient(circle_at_20%_0%,rgba(241,138,74,0.12),transparent_34%),linear-gradient(180deg,#1f1b18,#161311)]">
			<defs>
				<linearGradient id="routeGradient" x1="0" x2="1" y1="0" y2="1">
					<stop offset="0%" stop-color="#f08b50" />
					<stop offset="100%" stop-color="#f5efe5" />
				</linearGradient>
			</defs>
			{#each Array.from({ length: 6 }) as _, index}
				<line x1="0" y1={index * (preview.height / 5)} x2={preview.width} y2={index * (preview.height / 5)} stroke="rgba(245,239,229,0.06)" stroke-width="1" />
			{/each}
			<path d={preview.path} fill="none" stroke="url(#routeGradient)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
		</svg>
		<div class="mt-3 flex items-center justify-between text-xs uppercase tracking-[0.24em] text-paper/55">
			<span>Polyline data</span>
			<span>Imported Strava route</span>
		</div>
	</div>
{:else}
	<div class="rounded-[2rem] border border-dashed border-black/15 bg-[linear-gradient(180deg,rgba(255,255,255,0.74),rgba(245,239,232,0.88))] p-8 text-sm leading-6 text-slate">
		<p class="font-semibold text-ink">No route polyline available</p>
		<p class="mt-2 max-w-prose">This activity still loads, but the route preview will appear once the imported Strava payload includes map data.</p>
	</div>
{/if}