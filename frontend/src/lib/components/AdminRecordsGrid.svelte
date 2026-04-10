<script lang="ts">
	import type { AdminActivitySummary } from '$lib/api/admin';

	const distanceFormatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });
	const dateFormatter = new Intl.DateTimeFormat('en-GB', {
		weekday: 'short',
		day: '2-digit',
		month: 'short',
		year: 'numeric'
	});

	const fieldDefinitions = [
		{ key: 'athlete', label: 'Athlete', value: (record: AdminActivitySummary) => String(record.user_strava_athlete_id) },
		{ key: 'activity', label: 'Activity', value: (record: AdminActivitySummary) => record.name ?? `Activity ${record.strava_activity_id}` },
		{ key: 'date', label: 'When', value: (record: AdminActivitySummary) => dateFormatter.format(new Date(record.start_date)) },
		{ key: 'type', label: 'Type', value: (record: AdminActivitySummary) => record.type ?? 'Activity' },
		{ key: 'distance', label: 'Distance', value: (record: AdminActivitySummary) => (record.distance == null ? 'n/a' : `${distanceFormatter.format(record.distance / 1000)} km`) },
		{ key: 'moving_time', label: 'Moving time', value: (record: AdminActivitySummary) => formatDuration(record.moving_time) },
		{ key: 'elapsed_time', label: 'Elapsed time', value: (record: AdminActivitySummary) => formatDuration(record.elapsed_time) },
		{ key: 'elevation_gain', label: 'Elevation', value: (record: AdminActivitySummary) => formatMetric(record.elevation_gain, 'm') },
		{ key: 'country', label: 'Country', value: (record: AdminActivitySummary) => record.location_country ?? 'Global' },
		{ key: 'token_health', label: 'Token health', value: (record: AdminActivitySummary) => record.token_health },
		{ key: 'raw', label: 'Raw payload', value: (record: AdminActivitySummary) => (record.has_raw_payload ? 'Stored' : 'Missing') }
	] as const;

	type FieldKey = (typeof fieldDefinitions)[number]['key'];
	type FieldDefinition = (typeof fieldDefinitions)[number];

	const defaultSelection: Record<FieldKey, boolean> = {
		athlete: true,
		activity: true,
		date: true,
		type: true,
		distance: true,
		moving_time: false,
		elapsed_time: false,
		elevation_gain: false,
		country: true,
		token_health: true,
		raw: true
	};

	function createEmptyFilters(): Record<FieldKey, string> {
		return {
			athlete: '',
			activity: '',
			date: '',
			type: '',
			distance: '',
			moving_time: '',
			elapsed_time: '',
			elevation_gain: '',
			country: '',
			token_health: '',
			raw: ''
		};
	}

	export let records: AdminActivitySummary[] = [];

	let selectedFields: Record<FieldKey, boolean> = { ...defaultSelection };
	let filters: Record<FieldKey, string> = createEmptyFilters();

	function formatDuration(value: number | null): string {
		if (value == null) {
			return 'n/a';
		}

		const hours = Math.floor(value / 3600);
		const minutes = Math.floor((value % 3600) / 60);
		return `${hours > 0 ? `${hours}h ` : ''}${minutes}m`;
	}

	function formatMetric(value: number | null, suffix: string): string {
		if (value == null) {
			return 'n/a';
		}

		return `${distanceFormatter.format(value)} ${suffix}`;
	}

	function toggleField(key: FieldKey) {
		const nextValue = !selectedFields[key];
		selectedFields = { ...selectedFields, [key]: nextValue };
		if (!nextValue) {
			filters = { ...filters, [key]: '' };
		}
	}

	function selectDefaultFields() {
		selectedFields = { ...defaultSelection };
		filters = createEmptyFilters();
	}

	function selectAllFields() {
		selectedFields = fieldDefinitions.reduce((accumulator, field) => {
			accumulator[field.key] = true;
			return accumulator;
		}, {} as Record<FieldKey, boolean>);
	}

	function clearFilters() {
		filters = createEmptyFilters();
	}

	function updateFilter(key: FieldKey, value: string) {
		filters = { ...filters, [key]: value };
	}

	function getVisibleFields(): FieldDefinition[] {
		return fieldDefinitions.filter((field) => selectedFields[field.key]);
	}

	function getFilteredRecords(visibleFields: FieldDefinition[]): AdminActivitySummary[] {
		return records.filter((record) =>
			visibleFields.every((field) => {
				const filter = filters[field.key].trim().toLowerCase();
				if (!filter) {
					return true;
				}

				return field.value(record).toLowerCase().includes(filter);
			})
		);
	}

	async function exportXlsx(visibleFields: FieldDefinition[], filteredRecords: AdminActivitySummary[]) {
		const { utils, writeFile } = await import('xlsx');
		const rows = filteredRecords.map((record) =>
			visibleFields.reduce(
				(accumulator, field) => {
					accumulator[field.label] = field.value(record);
					return accumulator;
				},
				{} as Record<string, string>
			)
		);

		const workbook = utils.book_new();
		const worksheet = utils.json_to_sheet(rows);
		utils.book_append_sheet(workbook, worksheet, 'Admin Records');
		writeFile(workbook, `admin-records-${new Date().toISOString().slice(0, 10)}.xlsx`);
	}

	$: visibleFields = getVisibleFields();
	$: filteredRecords = getFilteredRecords(visibleFields);
	$: visibleCount = visibleFields.length;
</script>

<section class="surface-panel">
	<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
		<div>
			<p class="label-sharp">Data grid</p>
			<h3 class="section-title mt-2">Selectable fields, per-column filters, and XLSX export.</h3>
			<p class="section-subtitle">Pick the fields you want to inspect, filter the visible columns, and export the current filtered view.</p>
		</div>
		<div class="flex flex-wrap gap-2">
			<button class="action-button action-button--secondary" type="button" on:click={selectDefaultFields}>Default view</button>
			<button class="action-button action-button--secondary" type="button" on:click={selectAllFields}>All fields</button>
			<button class="action-button action-button--secondary" type="button" on:click={clearFilters}>Clear filters</button>
			<button class="action-button action-button--primary" type="button" on:click={() => void exportXlsx(visibleFields, filteredRecords)} disabled={filteredRecords.length === 0 || visibleCount === 0}>Export XLSX</button>
		</div>
	</div>

	<div class="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]">
		<div class="section-block">
			<p class="label-sharp">Visible fields</p>
			<div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
				{#each fieldDefinitions as field}
					<label class="flex items-center gap-3 border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-sm text-[var(--color-text)]">
						<input type="checkbox" checked={selectedFields[field.key]} on:change={() => toggleField(field.key)} />
						<span>{field.label}</span>
					</label>
				{/each}
			</div>
		</div>

		<div class="section-block">
			<p class="label-sharp">View summary</p>
			<div class="mt-4 grid gap-3 sm:grid-cols-2">
				<div>
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Visible columns</p>
					<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{visibleCount}</p>
				</div>
				<div>
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Matched rows</p>
					<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{filteredRecords.length}</p>
				</div>
				<div>
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Total rows</p>
					<p class="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text)]">{records.length}</p>
				</div>
				<div>
					<p class="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-text-muted)]">Export</p>
					<p class="mt-2 text-sm leading-6 text-[var(--color-text-muted)]">Filtered rows and visible fields only.</p>
				</div>
			</div>
		</div>
	</div>

	{#if visibleFields.length === 0}
		<div class="mt-6 border border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] p-4 text-sm leading-6 text-[var(--color-text-muted)]">
			Choose at least one field to view the grid.
		</div>
	{:else}
		<div class="mt-6 overflow-x-auto border border-[var(--color-border)] bg-[var(--color-surface)]">
			<table class="min-w-full text-left text-sm">
				<thead class="border-b border-[var(--color-border)] bg-[rgba(0,0,0,0.02)] text-xs uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
					<tr>
						{#each visibleFields as field}
							<th class="min-w-40 px-4 py-3 align-bottom">{field.label}</th>
						{/each}
					</tr>
					<tr>
						{#each visibleFields as field}
							<th class="px-4 pb-4 pt-0 align-top normal-case tracking-normal">
								<label class="flex flex-col gap-2">
									<span class="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--color-text-muted)]">Filter</span>
									<input class="input-sharp text-sm" type="text" value={filters[field.key]} placeholder={`Filter ${field.label.toLowerCase()}`} on:input={(event) => updateFilter(field.key, (event.currentTarget as HTMLInputElement).value)} />
								</label>
							</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#if filteredRecords.length === 0}
						<tr>
							<td class="px-4 py-6 text-sm leading-6 text-[var(--color-text-muted)]" colspan={visibleFields.length}>No rows match the current column filters.</td>
						</tr>
					{:else}
						{#each filteredRecords as record}
							<tr class="border-b border-[var(--color-border)] last:border-b-0">
								{#each visibleFields as field}
									<td class="px-4 py-3 align-top text-[var(--color-text)]">{field.value(record)}</td>
								{/each}
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</div>
	{/if}
</section>