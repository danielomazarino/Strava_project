<script lang="ts">
	import type { HeatmapTile } from '$lib/api/models';

	export let tile: HeatmapTile | null = null;

	const width = 960;
	const height = 540;
	const padding = 32;

	$: view = tile
		? tile.points.map((point) => {
			const lngSpan = Math.max(tile.bounds.max_lng - tile.bounds.min_lng, 0.0001);
			const latSpan = Math.max(tile.bounds.max_lat - tile.bounds.min_lat, 0.0001);
			const x = padding + ((point.lng - tile.bounds.min_lng) / lngSpan) * (width - padding * 2);
			const y = height - padding - ((point.lat - tile.bounds.min_lat) / latSpan) * (height - padding * 2);
			return { ...point, x, y };
		})
		: [];
</script>

{#if tile}
	<div class="overflow-hidden border border-black/10 bg-[#14120f] shadow-soft">
		<div class="flex items-center justify-between border-b border-black/10 px-4 py-3 text-xs uppercase tracking-[0.24em] text-paper/60">
			<span>Density canvas</span>
			<span>{tile.point_count} points · {tile.activity_count} activities</span>
		</div>
		<svg viewBox={`0 0 ${width} ${height}`} class="block h-auto w-full bg-[#1a1714]">
			<defs>
				<pattern id="tileGrid" width="48" height="48" patternUnits="userSpaceOnUse">
					<path d="M 48 0 L 0 0 0 48" fill="none" stroke="rgba(245,239,229,0.06)" stroke-width="1" />
				</pattern>
				<linearGradient id="tileGradient" x1="0" x2="1" y1="0" y2="1">
					<stop offset="0%" stop-color="#f08b50" stop-opacity="0.95" />
					<stop offset="100%" stop-color="#f5efe5" stop-opacity="0.85" />
				</linearGradient>
			</defs>
			<rect x="0" y="0" width={width} height={height} fill="#1a1714" />
			<rect x="0" y="0" width={width} height={height} fill="url(#tileGrid)" />
			{#if tile.point_count === 0}
				<g fill="#f5efe5" text-anchor="middle">
					<text x={width / 2} y={height / 2 - 8} font-size="24">No points in this view</text>
					<text x={width / 2} y={height / 2 + 24} fill="rgba(245,239,229,0.65)" font-size="14">Try another preset or widen the date range.</text>
				</g>
			{:else}
				{#each view as point}
					<circle cx={point.x} cy={point.y} r="8" fill="url(#tileGradient)" fill-opacity="0.8" />
				{/each}
			{/if}
		</svg>
	</div>
{:else}
	<div class="border border-dashed border-black/15 bg-white/70 p-8 text-sm leading-6 text-slate">
		<p class="font-semibold text-ink">No heatmap data</p>
		<p class="mt-2">Connect Strava from the sidebar system section, then choose a preset or adjust the filters to fetch the next density snapshot.</p>
	</div>
{/if}