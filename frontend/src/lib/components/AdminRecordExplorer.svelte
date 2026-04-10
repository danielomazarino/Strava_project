<script lang="ts">
	import type { AdminActivitySummary } from '$lib/api/admin';

	const dateFormatter = new Intl.DateTimeFormat('en-GB', {
		weekday: 'short',
		day: '2-digit',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});

	const numericFormatter = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1 });

	type ColumnKey =
		| 'athlete'
		| 'activity'
		| 'date'
		| 'type'
		| 'distance'
		| 'moving_time'
		| 'elapsed_time'
		| 'elevation_gain'
		| 'country'
		| 'token_health'
		| 'expand';

	type SortKey =
		| 'date'
		| 'activity'
		| 'athlete'
		| 'type'
		| 'distance'
		| 'moving_time'
		| 'elapsed_time'
		| 'elevation_gain'
		| 'country'
		| 'token_health';

	type FilterState = {
		query: string;
		type: string;
		country: string;
		tokenHealth: string;
	};

	type DetailRow = {
		label: string;
		value: string;
	};

	type QuickAction = 'quick-actions' | 'expand-all' | 'collapse-all' | 'reset-pinned' | 'reset-view' | 'export-xlsx';

	const columns: Array<{ key: ColumnKey; label: string; width: number; sortable?: boolean }> = [
		{ key: 'athlete', label: 'Athlete', width: 132, sortable: true },
		{ key: 'activity', label: 'Activity', width: 280, sortable: true },
		{ key: 'date', label: 'Date', width: 180, sortable: true },
		{ key: 'type', label: 'Type', width: 120, sortable: true },
		{ key: 'distance', label: 'Distance', width: 110, sortable: true },
		{ key: 'moving_time', label: 'Time', width: 110, sortable: true },
		{ key: 'elapsed_time', label: 'Elapsed', width: 110, sortable: true },
		{ key: 'elevation_gain', label: 'Elevation', width: 110, sortable: true },
		{ key: 'country', label: 'Country', width: 96, sortable: true },
		{ key: 'token_health', label: 'Token', width: 120, sortable: true },
		{ key: 'expand', label: '', width: 84 }
	];

	const sortableKeys: SortKey[] = ['date', 'activity', 'athlete', 'type', 'distance', 'moving_time', 'elapsed_time', 'elevation_gain', 'country', 'token_health'];
	const columnWidthMap = Object.fromEntries(columns.map((column) => [column.key, column.width])) as Record<ColumnKey, number>;
	const defaultPinnedColumns: ColumnKey[] = ['athlete', 'activity', 'date'];

	export let records: AdminActivitySummary[] = [];

	let filters: FilterState = {
		query: '',
		type: 'all',
		country: 'all',
		tokenHealth: 'all'
	};
	let quickAction: QuickAction = 'quick-actions';
	let sortKey: SortKey = 'date';
	let sortDirection: 'asc' | 'desc' = 'desc';
	let pinnedColumns: ColumnKey[] = [...defaultPinnedColumns];
	let expandedRecordIds = new Set<string>();

	function formatDistance(distance: number | null): string {
		if (distance == null) {
			return 'n/a';
		}

		return `${numericFormatter.format(distance / 1000)} km`;
	}

	function formatDuration(seconds: number | null): string {
		if (seconds == null) {
			return 'n/a';
		}

		const hours = Math.floor(seconds / 3600);
		const minutes = Math.floor((seconds % 3600) / 60);
		return `${hours > 0 ? `${hours}h ` : ''}${minutes}m`;
	}

	function formatMetric(value: number | null, suffix: string): string {
		if (value == null) {
			return 'n/a';
		}

		return `${numericFormatter.format(value)} ${suffix}`;
	}

	function formatJson(value: Record<string, unknown> | null): string {
		if (!value) {
			return 'No raw payload stored.';
		}

		return JSON.stringify(value, null, 2);
	}

	function normalize(text: unknown): string {
		if (text == null) {
			return '';
		}

		return String(text).toLowerCase();
	}

	function buildSearchIndex(record: AdminActivitySummary): string {
		return [
			record.id,
			record.user_id,
			record.user_strava_athlete_id,
			record.strava_activity_id,
			record.name,
			record.type,
			record.start_date,
			record.distance,
			record.moving_time,
			record.elapsed_time,
			record.elevation_gain,
			record.description,
			record.polyline,
			record.timezone,
			record.location_country,
			record.token_health,
			record.created_at,
			record.updated_at,
			record.raw_payload ? JSON.stringify(record.raw_payload) : ''
		]
			.map(normalize)
			.join(' ');
	}

	function isExpanded(recordId: string): boolean {
		return expandedRecordIds.has(recordId);
	}

	function toggleExpanded(recordId: string) {
		const nextExpanded = new Set(expandedRecordIds);
		if (nextExpanded.has(recordId)) {
			nextExpanded.delete(recordId);
		} else {
			nextExpanded.add(recordId);
		}

		expandedRecordIds = nextExpanded;
	}

	function expandAll() {
		expandedRecordIds = new Set(filteredRecords.map((record) => record.id));
	}

	function collapseAll() {
		expandedRecordIds = new Set();
	}

	function handleQuickAction(event: Event) {
		const select = event.currentTarget as HTMLSelectElement;
		const action = select.value as QuickAction;

		switch (action) {
			case 'expand-all':
				expandAll();
				break;
			case 'collapse-all':
				collapseAll();
				break;
			case 'reset-pinned':
				resetPinnedColumns();
				break;
			case 'reset-view':
				clearFilters();
				break;
			case 'export-xlsx':
				if (visibleRecords.length > 0) {
					void exportXlsx();
				}
				break;
		}

		quickAction = 'quick-actions';
		select.value = 'quick-actions';
	}

	function clearFilters() {
		filters = {
			query: '',
			type: 'all',
			country: 'all',
			tokenHealth: 'all'
		};
		sortKey = 'date';
		sortDirection = 'desc';
	}

	function setSortDirection(value: 'asc' | 'desc') {
		sortDirection = value;
	}

	function resetPinnedColumns() {
		pinnedColumns = [...defaultPinnedColumns];
	}

	function togglePin(columnKey: ColumnKey) {
		if (columnKey === 'expand') {
			return;
		}

		if (pinnedColumns.includes(columnKey)) {
			pinnedColumns = pinnedColumns.filter((entry) => entry !== columnKey);
			return;
		}

		pinnedColumns = [...pinnedColumns, columnKey];
	}

	function getPinnedLeft(columnKey: ColumnKey): number {
		let offset = 0;
		for (const entry of columns) {
			if (entry.key === columnKey) {
				break;
			}

			if (pinnedColumns.includes(entry.key)) {
				offset += columnWidthMap[entry.key];
			}
		}

		return offset;
	}

	function sortValue(record: AdminActivitySummary, key: SortKey): string | number {
		switch (key) {
			case 'date':
				return new Date(record.start_date).getTime();
			case 'activity':
				return normalize(record.name ?? `Activity ${record.strava_activity_id}`);
			case 'athlete':
				return record.user_strava_athlete_id;
			case 'type':
				return normalize(record.type ?? '');
			case 'distance':
				return record.distance ?? -1;
			case 'moving_time':
				return record.moving_time ?? -1;
			case 'elapsed_time':
				return record.elapsed_time ?? -1;
			case 'elevation_gain':
				return record.elevation_gain ?? -1;
			case 'country':
				return normalize(record.location_country ?? 'Global');
			case 'token_health':
				return normalize(record.token_health);
		}
	}

	function compareValues(left: string | number, right: string | number): number {
		if (typeof left === 'number' && typeof right === 'number') {
			return left - right;
		}

		return String(left).localeCompare(String(right));
	}

	$: uniqueTypes = Array.from(new Set(records.map((record) => record.type).filter(Boolean) as string[])).sort();
	$: uniqueCountries = Array.from(new Set(records.map((record) => record.location_country).filter(Boolean) as string[])).sort();
	$: searchTerm = normalize(filters.query);
	$: filteredRecords = records.filter((record) => {
		const matchesSearch = searchTerm.length === 0 || buildSearchIndex(record).includes(searchTerm);
		const matchesType = filters.type === 'all' || normalize(record.type) === normalize(filters.type);
		const matchesCountry = filters.country === 'all' || normalize(record.location_country) === normalize(filters.country);
		const matchesTokenHealth = filters.tokenHealth === 'all' || normalize(record.token_health) === normalize(filters.tokenHealth);

		return matchesSearch && matchesType && matchesCountry && matchesTokenHealth;
	});
	$: sortedRecords = [...filteredRecords].sort((left, right) => {
		const leftValue = sortValue(left, sortKey);
		const rightValue = sortValue(right, sortKey);
		const comparison = compareValues(leftValue, rightValue);
		return sortDirection === 'asc' ? comparison : -comparison;
	});
	$: visibleRecords = sortedRecords;
	$: visibleRecordCount = visibleRecords.length;
	$: recordCount = records.length;
	$: pinnedLabel = pinnedColumns.length === 0 ? 'No pinned columns' : `${pinnedColumns.length} pinned`;

	function detailRows(record: AdminActivitySummary): DetailRow[] {
		return [
			{ label: 'Activity id', value: record.id },
			{ label: 'User id', value: record.user_id },
			{ label: 'Athlete id', value: String(record.user_strava_athlete_id) },
			{ label: 'Strava activity id', value: String(record.strava_activity_id) },
			{ label: 'Start date', value: new Date(record.start_date).toLocaleString('en-GB') },
			{ label: 'Type', value: record.type ?? 'n/a' },
			{ label: 'Name', value: record.name ?? 'n/a' },
			{ label: 'Distance', value: formatDistance(record.distance) },
			{ label: 'Moving time', value: formatDuration(record.moving_time) },
			{ label: 'Elapsed time', value: formatDuration(record.elapsed_time) },
			{ label: 'Elevation gain', value: formatMetric(record.elevation_gain, 'm') },
			{ label: 'Description', value: record.description ?? 'n/a' },
			{ label: 'Timezone', value: record.timezone ?? 'n/a' },
			{ label: 'Country', value: record.location_country ?? 'n/a' },
			{ label: 'Token health', value: record.token_health },
			{ label: 'Has raw payload', value: record.has_raw_payload ? 'Yes' : 'No' },
			{ label: 'Created at', value: record.created_at ? new Date(record.created_at).toLocaleString('en-GB') : 'n/a' },
			{ label: 'Updated at', value: record.updated_at ? new Date(record.updated_at).toLocaleString('en-GB') : 'n/a' },
			{ label: 'Polyline', value: record.polyline ?? 'n/a' }
		];
	}

	function asCell(value: string | number | boolean | null): string {
		return value == null ? '' : String(value);
	}

	async function exportXlsx() {
		const { utils, writeFile } = await import('xlsx');
		const rows = visibleRecords.map((record) => ({
			activity_id: asCell(record.id),
			user_id: asCell(record.user_id),
			user_strava_athlete_id: asCell(record.user_strava_athlete_id),
			strava_activity_id: asCell(record.strava_activity_id),
			name: asCell(record.name),
			type: asCell(record.type),
			start_date: asCell(record.start_date),
			distance: asCell(record.distance),
			moving_time: asCell(record.moving_time),
			elapsed_time: asCell(record.elapsed_time),
			elevation_gain: asCell(record.elevation_gain),
			description: asCell(record.description),
			polyline: asCell(record.polyline),
			timezone: asCell(record.timezone),
			location_country: asCell(record.location_country),
			token_health: asCell(record.token_health),
			has_raw_payload: asCell(record.has_raw_payload),
			created_at: asCell(record.created_at),
			updated_at: asCell(record.updated_at),
			raw_payload: asCell(record.raw_payload ? JSON.stringify(record.raw_payload) : '')
		}));

		const workbook = utils.book_new();
		const worksheet = utils.json_to_sheet(rows);
		utils.book_append_sheet(workbook, worksheet, 'Admin Records');
		writeFile(workbook, `admin-records-${new Date().toISOString().slice(0, 10)}.xlsx`);
	}
</script>

<section class="surface-panel">
	<div class="flex flex-col gap-5">
		<div class="flex flex-col gap-3 xl:flex-row xl:items-end xl:justify-between">
			<div>
				<p class="label-sharp">Record browser</p>
				<h3 class="section-title mt-2">Full dataset, no reduction.</h3>
				<p class="section-subtitle">Search every field, sort any core column, pin the important ones, and expand a row to see the full activity payload.</p>
			</div>
			<div class="flex flex-col gap-2 sm:min-w-[18rem]">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Quick actions</span>
				<select class="input-sharp" bind:value={quickAction} on:change={handleQuickAction}>
					<option value="quick-actions" disabled>Expand, reset, export...</option>
					<option value="expand-all">Expand all rows</option>
					<option value="collapse-all">Collapse all rows</option>
					<option value="reset-pinned">Reset pinned columns</option>
					<option value="reset-view">Reset filters and sort</option>
					<option value="export-xlsx">Export visible rows</option>
				</select>
			</div>
		</div>

		<div class="flex flex-wrap items-center gap-3 text-sm text-[var(--color-text-muted)]">
			<span>{recordCount} total records</span>
			<span>•</span>
			<span>{visibleRecordCount} visible after filters</span>
			<span>•</span>
			<span>{pinnedLabel}</span>
			<span>•</span>
			<span>{records.filter((record) => record.has_raw_payload).length} with raw payloads</span>
		</div>

		<div class="grid gap-3 lg:grid-cols-[minmax(0,1.25fr)_220px_220px_220px_220px]">
			<label class="flex flex-col gap-2 lg:col-span-1">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Search every field</span>
				<input class="input-sharp" type="text" bind:value={filters.query} placeholder="Search name, description, raw payload, country, timezone..." />
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Sort by</span>
				<select class="input-sharp" bind:value={sortKey}>
					{#each sortableKeys as key}
						<option value={key}>{key.replace('_', ' ')}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Direction</span>
				<select class="input-sharp" bind:value={sortDirection} on:change={(event) => setSortDirection((event.currentTarget as HTMLSelectElement).value as 'asc' | 'desc')}>
					<option value="desc">Newest / highest first</option>
					<option value="asc">Oldest / lowest first</option>
				</select>
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Type</span>
				<select class="input-sharp" bind:value={filters.type}>
					<option value="all">All types</option>
					{#each uniqueTypes as type}
						<option value={type}>{type}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col gap-2">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Country</span>
				<select class="input-sharp" bind:value={filters.country}>
					<option value="all">All countries</option>
					{#each uniqueCountries as country}
						<option value={country}>{country}</option>
					{/each}
				</select>
			</label>
			<label class="flex flex-col gap-2 lg:col-span-2">
				<span class="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">Token health</span>
				<select class="input-sharp" bind:value={filters.tokenHealth}>
					<option value="all">All token states</option>
					<option value="active">active</option>
					<option value="expiring">expiring</option>
					<option value="expired">expired</option>
				</select>
			</label>
		</div>

		<div class="grid gap-3">
			<p class="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--color-text-muted)]">Pin columns</p>
			<div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
				{#each columns.filter((column) => column.key !== 'expand') as column}
					<label class="flex items-center gap-3 border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-sm text-[var(--color-text)]">
						<input type="checkbox" checked={pinnedColumns.includes(column.key)} on:change={() => togglePin(column.key)} />
						<span>{column.label}</span>
					</label>
				{/each}
			</div>
		</div>
	</div>

	{#if visibleRecords.length === 0}
		<div class="mt-6 border border-[var(--color-border)] bg-[var(--color-surface)] p-6 text-sm leading-6 text-[var(--color-text-muted)]">
			No records match the current search and filters.
		</div>
	{:else}
		<div class="mt-6 overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface)]">
			<div class="overflow-x-auto">
				<table class="min-w-[1160px] w-full text-left text-sm">
					<thead class="sticky top-0 z-30 bg-[var(--color-surface)] text-xs uppercase tracking-[0.18em] text-[var(--color-text-muted)]">
						<tr class="border-b border-[var(--color-border)]">
							{#each columns as column}
								<th
									class={`px-4 py-3 ${pinnedColumns.includes(column.key) ? 'sticky z-40 bg-[var(--color-surface)]' : ''}`}
									style={`width:${column.width}px; min-width:${column.width}px; ${pinnedColumns.includes(column.key) ? `left:${getPinnedLeft(column.key)}px;` : ''}`}
								>
									<span>{column.label || ' '}</span>
								</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each visibleRecords as record}
							<tr class="border-b border-[var(--color-border)] align-top hover:bg-[rgba(0,0,0,0.015)]">
								{#each columns as column}
									<td
										class={`px-4 py-4 align-top ${pinnedColumns.includes(column.key) ? 'sticky z-20 bg-[var(--color-surface)]' : ''}`}
										style={`width:${column.width}px; min-width:${column.width}px; ${pinnedColumns.includes(column.key) ? `left:${getPinnedLeft(column.key)}px;` : ''}`}
									>
										{#if column.key === 'athlete'}
											<div class="font-semibold text-[var(--color-text)]">{record.user_strava_athlete_id}</div>
											<div class="mt-1 text-xs uppercase tracking-[0.16em] text-[var(--color-text-muted)]">{record.user_id}</div>
										{:else if column.key === 'activity'}
											<div class="font-semibold text-[var(--color-text)]">{record.name ?? `Activity ${record.strava_activity_id}`}</div>
											<div class="mt-1 text-xs uppercase tracking-[0.16em] text-[var(--color-text-muted)]">{record.strava_activity_id}</div>
										{:else if column.key === 'date'}
											<div class="font-medium text-[var(--color-text)]">{dateFormatter.format(new Date(record.start_date))}</div>
										{:else if column.key === 'type'}
											{record.type ?? 'n/a'}
										{:else if column.key === 'distance'}
											{formatDistance(record.distance)}
										{:else if column.key === 'moving_time'}
											{formatDuration(record.moving_time)}
										{:else if column.key === 'elapsed_time'}
											{formatDuration(record.elapsed_time)}
										{:else if column.key === 'elevation_gain'}
											{formatMetric(record.elevation_gain, 'm')}
										{:else if column.key === 'country'}
											{record.location_country ?? 'Global'}
										{:else if column.key === 'token_health'}
											<span class="inline-flex items-center rounded-full border border-[var(--color-border)] bg-[rgba(252,76,2,0.06)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-text)]">
												{record.token_health}
											</span>
										{:else}
											<span
												class="inline-flex cursor-pointer items-center rounded border border-[var(--color-border)] px-2 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--color-text)] transition-colors hover:bg-[rgba(0,0,0,0.03)]"
												role="button"
												tabindex="0"
												on:click={() => toggleExpanded(record.id)}
												on:keydown={(event) => {
													if (event.key === 'Enter' || event.key === ' ') {
														event.preventDefault();
														toggleExpanded(record.id);
													}
												}}
											>
												{isExpanded(record.id) ? 'Hide' : 'View'}
											</span>
										{/if}
									</td>
								{/each}
							</tr>

							{#if isExpanded(record.id)}
								<tr class="border-b border-[var(--color-border)] bg-[rgba(0,0,0,0.015)]">
									<td class="px-4 py-5" colspan={columns.length}>
										<div class="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(0,0.92fr)]">
											<div>
												<p class="label-sharp">Full record</p>
												<dl class="mt-4 divide-y divide-[var(--color-border)] border-y border-[var(--color-border)]">
													{#each detailRows(record) as row}
														<div class="grid gap-3 py-3 md:grid-cols-[220px_minmax(0,1fr)]">
															<dt class="text-[11px] font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">{row.label}</dt>
															<dd class="break-words text-sm leading-6 text-[var(--color-text)]">{row.value}</dd>
														</div>
													{/each}
												</dl>
											</div>
											<div>
												<p class="label-sharp">Raw payload</p>
												<pre class="mt-4 max-h-[34rem] overflow-auto border border-[var(--color-border)] bg-[var(--color-bg)] p-4 text-xs leading-6 text-[var(--color-text)]">{formatJson(record.raw_payload)}</pre>
											</div>
										</div>
									</td>
								</tr>
							{/if}
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</section>