<script lang="ts">
	import { onMount } from 'svelte';
	import PageShell from '$lib/ui/PageShell.svelte';
	import { DEMO_STRAVA_ATHLETE_ID, session } from '$lib/stores/session';
	import { getHeatmapTile } from '$lib/api/heatmaps';
	import type { HeatmapTile } from '$lib/api/models';
	import HeatmapTileView from '$lib/components/HeatmapTileView.svelte';

	type Point = {
		x: number;
		y: number;
	};

	type GestureMode = 'idle' | 'drag' | 'pinch';

	type HeatmapPreset = {
		label: string;
		description: string;
		z: number;
		x: number;
		y: number;
	};

	type IntensityMode = 'All' | 'Distance' | 'Time';

	const presets: HeatmapPreset[] = [
		{ label: 'World', description: 'Start broad and see the full imported footprint.', z: 1, x: 1, y: 1 },
		{ label: 'Europe', description: 'A regional sweep for quicker pattern spotting.', z: 4, x: 8, y: 5 },
		{ label: 'Sweden', description: 'A national view around the main activity clusters.', z: 5, x: 17, y: 10 },
		{ label: 'Gothenburg', description: 'A city-level view for the default density snapshot.', z: 6, x: 33, y: 20 },
		{ label: 'My Routes', description: 'A tighter local view for route-heavy sessions.', z: 7, x: 66, y: 40 }
	];

	const minZoom = 1;
	const maxZoom = 16;
	const defaultPreset = presets[3];
	const intensityModes: IntensityMode[] = ['All', 'Distance', 'Time'];
	const dragThresholdPx = 120;
	const pinchZoomInThreshold = 1.16;
	const pinchZoomOutThreshold = 0.84;
	const maxPanSteps = 3;

	let loading = false;
	let error = '';
	let tile: HeatmapTile | null = null;
	let z = defaultPreset.z;
	let x = defaultPreset.x;
	let y = defaultPreset.y;
	let startDate = '';
	let endDate = '';
	let activityType = '';
	let country = '';
	let intensity: IntensityMode = intensityModes[0];
	let selectedPreset = defaultPreset.label;
	let requestToken = 0;
	let dragOffsetX = 0;
	let dragOffsetY = 0;
	let pinchScale = 1;
	let gestureMode: GestureMode = 'idle';
	let dragStart: Point | null = null;
	let pinchStartCenter: Point | null = null;
	let pinchStartDistance = 0;
	let surfaceTransform = '';
	let activePointers = new Map<number, Point>();

	$: surfaceTransform = `transform: translate3d(${dragOffsetX}px, ${dragOffsetY}px, 0) scale(${pinchScale}); transition: ${gestureMode === 'idle' ? 'transform 180ms ease-out' : 'none'};`;

	function setDefaults() {
		const now = new Date();
		const start = new Date(now);
		start.setDate(start.getDate() - 180);
		startDate = start.toISOString().slice(0, 10);
		endDate = now.toISOString().slice(0, 10);
	}

	function clamp(value: number, lower: number, upper: number) {
		return Math.min(Math.max(value, lower), upper);
	}

	function maxTileIndex(level: number) {
		return 2 ** level - 1;
	}

	function getCurrentPointerPoints() {
		return [...activePointers.values()];
	}

	function getDistance(firstPoint: Point, secondPoint: Point) {
		return Math.hypot(secondPoint.x - firstPoint.x, secondPoint.y - firstPoint.y);
	}

	function getCenter(firstPoint: Point, secondPoint: Point) {
		return {
			x: (firstPoint.x + secondPoint.x) / 2,
			y: (firstPoint.y + secondPoint.y) / 2
		};
	}

	function getZoomedView(delta: number) {
		const nextZoom = clamp(z + delta, minZoom, maxZoom);
		if (nextZoom === z) {
			return { nextZoom, nextX: x, nextY: y };
		}

		if (delta > 0) {
			return { nextZoom, nextX: x * 2 + 1, nextY: y * 2 + 1 };
		}

		return { nextZoom, nextX: Math.floor((x - 1) / 2), nextY: Math.floor((y - 1) / 2) };
	}

	function resetGestureState(nextMode: GestureMode = 'idle') {
		gestureMode = nextMode;
		dragStart = null;
		pinchStartCenter = null;
		pinchStartDistance = 0;
		dragOffsetX = 0;
		dragOffsetY = 0;
		pinchScale = 1;
	}

	function commitGesture() {
		const panStepsX = clamp(Math.round(dragOffsetX / dragThresholdPx), -maxPanSteps, maxPanSteps);
		const panStepsY = clamp(Math.round(dragOffsetY / dragThresholdPx), -maxPanSteps, maxPanSteps);
		const zoomDelta = pinchScale >= pinchZoomInThreshold ? 1 : pinchScale <= pinchZoomOutThreshold ? -1 : 0;
		const zoomed = getZoomedView(zoomDelta);
		const limit = maxTileIndex(zoomed.nextZoom);
		const nextX = clamp(zoomed.nextX - panStepsX, 0, limit);
		const nextY = clamp(zoomed.nextY - panStepsY, 0, limit);

		if (zoomDelta !== 0 || panStepsX !== 0 || panStepsY !== 0) {
			applyView(zoomed.nextZoom, nextX, nextY);
		}
	}

	function refreshGestureFromPointers() {
		const points = getCurrentPointerPoints();
		if (points.length === 1 && dragStart) {
			const current = points[0];
			dragOffsetX = current.x - dragStart.x;
			dragOffsetY = current.y - dragStart.y;
			gestureMode = 'drag';
			return;
		}

		if (points.length >= 2 && pinchStartCenter && pinchStartDistance > 0) {
			const currentCenter = getCenter(points[0], points[1]);
			dragOffsetX = currentCenter.x - pinchStartCenter.x;
			dragOffsetY = currentCenter.y - pinchStartCenter.y;
			pinchScale = clamp(getDistance(points[0], points[1]) / pinchStartDistance, 0.78, 1.32);
			gestureMode = 'pinch';
		}
	}

	function handlePointerDown(event: PointerEvent) {
		if (event.pointerType === 'mouse' && event.button !== 0) {
			return;
		}

		const target = event.currentTarget as HTMLElement | null;
		try {
			target?.setPointerCapture(event.pointerId);
		} catch {
			// Pointer capture is best-effort for synthetic and embedded browser events.
		}
		activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });

		if (activePointers.size === 1) {
			gestureMode = 'drag';
			dragStart = { x: event.clientX, y: event.clientY };
			dragOffsetX = 0;
			dragOffsetY = 0;
			pinchScale = 1;
			return;
		}

		if (activePointers.size >= 2) {
			const [firstPoint, secondPoint] = getCurrentPointerPoints();
			gestureMode = 'pinch';
			pinchStartCenter = getCenter(firstPoint, secondPoint);
			pinchStartDistance = getDistance(firstPoint, secondPoint);
			dragStart = null;
			dragOffsetX = 0;
			dragOffsetY = 0;
			pinchScale = 1;
		}
	}

	function handlePointerMove(event: PointerEvent) {
		if (!activePointers.has(event.pointerId)) {
			return;
		}

		activePointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
		refreshGestureFromPointers();
	}

	function handlePointerEnd(event: PointerEvent) {
		activePointers.delete(event.pointerId);

		if (activePointers.size === 0) {
			commitGesture();
			resetGestureState();
			return;
		}

		if (gestureMode === 'pinch') {
			commitGesture();
			resetGestureState('drag');
			const [remainingPoint] = getCurrentPointerPoints();
			dragStart = remainingPoint ?? null;
			if (remainingPoint) {
				dragOffsetX = 0;
				dragOffsetY = 0;
			}
			return;
		}

		if (activePointers.size === 1) {
			const [remainingPoint] = getCurrentPointerPoints();
			dragStart = remainingPoint ?? null;
			dragOffsetX = 0;
			dragOffsetY = 0;
		}
	}

	function handleWheel(event: WheelEvent) {
		event.preventDefault();
		const zoomDirection = event.deltaY > 0 ? -1 : 1;
		const zoomed = getZoomedView(zoomDirection);
		applyView(zoomed.nextZoom, zoomed.nextX, zoomed.nextY);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'ArrowLeft') {
			event.preventDefault();
			moveTile(-1, 0);
			return;
		}

		if (event.key === 'ArrowRight') {
			event.preventDefault();
			moveTile(1, 0);
			return;
		}

		if (event.key === 'ArrowUp') {
			event.preventDefault();
			moveTile(0, -1);
			return;
		}

		if (event.key === 'ArrowDown') {
			event.preventDefault();
			moveTile(0, 1);
			return;
		}

		if (event.key === '+' || event.key === '=') {
			event.preventDefault();
			zoom(1);
			return;
		}

		if (event.key === '-') {
			event.preventDefault();
			zoom(-1);
		}
	}

	function applyView(nextZoom: number, nextX: number, nextY: number, presetLabel = 'Custom view') {
		z = clamp(nextZoom, minZoom, maxZoom);
		const limit = maxTileIndex(z);
		x = clamp(nextX, 0, limit);
		y = clamp(nextY, 0, limit);
		selectedPreset = presetLabel;
		void loadTile();
	}

	function selectPreset(preset: HeatmapPreset) {
		applyView(preset.z, preset.x, preset.y, preset.label);
	}

	function selectPresetByLabel(label: string) {
		const preset = presets.find((candidate) => candidate.label === label) ?? defaultPreset;
		selectPreset(preset);
	}

	function moveTile(deltaX: number, deltaY: number) {
		applyView(z, x + deltaX, y + deltaY);
	}

	function zoom(delta: number) {
		const nextZoom = clamp(z + delta, minZoom, maxZoom);
		if (nextZoom === z) {
			return;
		}

		if (delta > 0) {
			applyView(nextZoom, x * 2 + 1, y * 2 + 1);
			return;
		}

		applyView(nextZoom, Math.floor((x - 1) / 2), Math.floor((y - 1) / 2));
	}

	async function loadTile() {
		const token = ++requestToken;
		loading = true;
		error = '';
		const athleteId = $session?.stravaAthleteId ?? DEMO_STRAVA_ATHLETE_ID;
		try {
			const response = await getHeatmapTile(z, x, y, {
				stravaAthleteId: athleteId,
				startDate: startDate ? new Date(`${startDate}T00:00:00Z`) : undefined,
				endDate: endDate ? new Date(`${endDate}T23:59:59Z`) : undefined,
				activityType: activityType || undefined,
				country: country || undefined
			});

			if (token === requestToken) {
				tile = response.tile;
			}
		} catch (caught) {
			if (token === requestToken) {
				error = caught instanceof Error ? caught.message : 'Unable to load heatmap view';
			}
		} finally {
			if (token === requestToken) {
				loading = false;
			}
		}
	}

	$: scaleLabel = z <= 2 ? 'World' : z <= 4 ? 'Regional' : z <= 6 ? 'City' : 'Local';

	onMount(() => {
		setDefaults();
		void loadTile();
	});
</script>

<svelte:head>
	<title>Heatmap</title>
</svelte:head>

<PageShell title="Heatmap" subtitle="Explore your training visually.">
	<section class="surface-panel">
		<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
			<div>
				<p class="label-sharp">Map density explorer</p>
				<h2 class="section-title mt-2">Explore your training visually.</h2>
				<p class="section-subtitle">Tap a preset or use the canvas controls to move through the map without touching raw coordinates.</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<button class="action-button action-button--primary" on:click={() => void loadTile()}>Refresh view</button>
				<button class="action-button action-button--secondary" on:click={() => selectPreset(defaultPreset)}>Reset to Gothenburg</button>
			</div>
		</div>
	</section>

	<section class="grid items-start gap-6 xl:grid-cols-[minmax(0,3fr)_minmax(320px,1fr)]">
		<section class="surface-panel overflow-hidden p-0">
			<div class="flex flex-col gap-3 border-b border-[var(--color-border)] px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
				<div>
					<p class="label-sharp">Map canvas</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Drag, pinch, wheel, or use the keyboard to move the map. Presets are still there for quick jumps.</p>
				</div>
				<div class="flex flex-wrap items-center gap-2">
					<span class="inline-flex items-center border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--color-text-muted)]">{selectedPreset}</span>
					<span class="inline-flex items-center border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--color-text-muted)]">{scaleLabel}</span>
					{#if intensity !== 'All'}
						<span class="inline-flex items-center border border-[var(--color-accent)] bg-[rgba(252,76,2,0.08)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.24em] text-[var(--color-accent)]">{intensity} focus</span>
					{/if}
				</div>
			</div>

			<button
				type="button"
				class={`relative block w-full border-0 bg-[#0f1618] p-0 text-left [touch-action:none] [overscroll-behavior:contain] [user-select:none] ${gestureMode === 'idle' ? 'cursor-grab' : 'cursor-grabbing'}`}
				aria-label="Heatmap canvas. Drag, pinch, wheel, or use the arrow keys to move through the map."
				on:pointerdown={handlePointerDown}
				on:pointermove={handlePointerMove}
				on:pointerup={handlePointerEnd}
				on:pointercancel={handlePointerEnd}
				on:wheel={handleWheel}
				on:keydown={handleKeydown}
			>
				<div class="px-4 pt-4">
					<div class="section-block">
						<p class="label-sharp">Touch-first navigation</p>
						<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Drag to pan, pinch or wheel to zoom, and use the preset selector for quick jumps.</p>
					</div>
				</div>

				<div class="p-4 pb-6">
					<div class="overflow-hidden">
						<div class="origin-center will-change-transform" style={surfaceTransform}>
							<HeatmapTileView {tile} />
						</div>
					</div>
				</div>
			</button>
		</section>

		<div class="surface-panel space-y-5">
			<div class="grid gap-4">
				<div>
					<p class="label-sharp">Filters</p>
					<div class="mt-3 grid gap-3 md:grid-cols-2">
						<label class="flex flex-col gap-2"><span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Start date</span><input bind:value={startDate} type="date" class="input-sharp" /></label>
						<label class="flex flex-col gap-2"><span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">End date</span><input bind:value={endDate} type="date" class="input-sharp" /></label>
						<label class="flex flex-col gap-2 md:col-span-2"><span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Activity type</span><input bind:value={activityType} class="input-sharp" placeholder="Run, Ride, ..." /></label>
						<label class="flex flex-col gap-2 md:col-span-2"><span class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Country</span><input bind:value={country} class="input-sharp" placeholder="GB" /></label>
					</div>
				</div>

				<div>
					<p class="label-sharp">Preset</p>
					<div class="mt-3 grid gap-2 sm:grid-cols-[minmax(0,1fr)_auto_auto]">
						<select bind:value={selectedPreset} class="input-sharp" on:change={() => selectPresetByLabel(selectedPreset)}>
							{#each presets as preset}
								<option value={preset.label}>{preset.label}</option>
							{/each}
						</select>
						<button class="action-button action-button--secondary" on:click={() => selectPresetByLabel(selectedPreset)}>Go</button>
						<button class="action-button action-button--secondary" on:click={() => selectPreset(defaultPreset)}>Reset</button>
					</div>
				</div>

				<div>
					<p class="label-sharp">Map controls</p>
					<div class="mt-3 grid grid-cols-2 gap-2">
						<button class="action-button action-button--secondary" on:click={() => zoom(-1)}>Zoom out</button>
						<button class="action-button action-button--secondary" on:click={() => zoom(1)}>Zoom in</button>
					</div>
					<p class="mt-3 text-xs leading-6 text-[var(--color-text-muted)]">Use the arrow keys for panning. The on-screen controls stay small on purpose.</p>
				</div>
			</div>

			<p class="text-sm leading-6 text-[var(--color-text-muted)]">Drag, pinch, wheel, or use arrow keys for the main interaction. Filters only narrow the snapshot; they do not change the map controls.</p>

			{#if loading}
				<div class="surface-panel min-h-44 animate-pulse"></div>
			{:else if error}
				<div class="border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] p-4 text-sm text-[var(--color-text)]">{error}</div>
			{/if}
		</div>
	</section>
</PageShell>