<script lang="ts">
	import type { DiaryEntry } from '$lib/api/models';

	export let entry: DiaryEntry;

	const formatDate = new Intl.DateTimeFormat('en-GB', {
		weekday: 'short',
		day: '2-digit',
		month: 'short',
		year: 'numeric'
	});

	const formatDistance = new Intl.NumberFormat('en-GB', {
		maximumFractionDigits: 1,
		minimumFractionDigits: 1
	});

	$: distanceLabel = entry.distance == null ? 'Distance unknown' : `${formatDistance.format(entry.distance / 1000)} km`;
</script>

<a class="group block overflow-hidden rounded-[2rem] border border-white/60 bg-white/80 shadow-soft transition duration-300 hover:-translate-y-1 hover:shadow-glow" href={`/diary/${entry.strava_activity_id}`}>
	<div class="grid gap-0 md:grid-cols-[1fr_auto]">
		<div class="relative p-5 md:p-6">
			<div class="absolute left-0 top-0 h-full w-1 bg-[linear-gradient(180deg,rgba(241,138,74,0.9),rgba(35,79,67,0.75))]"></div>
			<div class="flex items-start justify-between gap-4 pl-2">
				<div>
					<p class="kicker">{entry.type ?? 'Activity'}</p>
					<h3 class="mt-2 font-display text-3xl leading-tight text-ink transition group-hover:text-ember">
						{entry.name ?? `Activity ${entry.strava_activity_id}`}
					</h3>
				</div>
				<div class="rounded-full border border-black/10 bg-[rgba(35,79,67,0.08)] px-3 py-1 text-xs font-bold uppercase tracking-[0.24em] text-pine">
					{entry.location_country ?? 'Global'}
				</div>
			</div>

			<div class="mt-5 flex flex-wrap gap-2 text-sm text-slate pl-2">
				<span class="rounded-full border border-black/10 bg-white/80 px-3 py-1">{distanceLabel}</span>
				<span class="rounded-full border border-black/10 bg-white/80 px-3 py-1">{formatDate.format(new Date(entry.start_date))}</span>
				{#if entry.moving_time}
					<span class="rounded-full border border-black/10 bg-white/80 px-3 py-1">{Math.round(entry.moving_time / 60)} min</span>
				{/if}
			</div>

			{#if entry.description}
				<p class="mt-4 max-w-3xl text-sm leading-7 text-slate pl-2">{entry.description}</p>
			{:else}
				<p class="mt-4 max-w-3xl text-sm leading-7 text-slate pl-2">Open to see the full activity detail and route preview.</p>
			{/if}
		</div>

		<div class="flex items-center gap-3 border-t border-white/60 bg-[linear-gradient(180deg,rgba(245,239,232,0.8),rgba(255,255,255,0.94))] px-5 py-4 md:flex-col md:justify-center md:border-l md:border-t-0 md:px-6 md:py-6">
			<div class="text-left md:text-center">
				<p class="text-[0.68rem] font-extrabold uppercase tracking-[0.34em] text-slate">Open activity</p>
				<p class="mt-1 text-sm text-ink">Route and detail view</p>
			</div>
			<div class="ml-auto flex h-11 w-11 items-center justify-center rounded-full bg-ink text-paper transition group-hover:translate-x-0.5 md:ml-0">
				<span aria-hidden="true">↗</span>
			</div>
		</div>
	</div>
</a>