<script lang="ts">
	import { page } from '$app/stores';
	import { session, getSessionDisplayName } from '$lib/stores/session';
	import NavLink from '$lib/ui/NavLink.svelte';

	export let title = 'Strava Training Diary';

	type NavItem = {
		href: string;
		label: string;
		icon: 'dashboard' | 'insights' | 'ask' | 'compare' | 'diary' | 'charts' | 'heatmap' | 'routes' | 'settings' | 'auth' | 'about';
		variant: 'primary' | 'secondary';
	};

	type NavSection = {
		key: 'ai' | 'training' | 'maps' | 'system';
		label: string;
		ariaLabel: string;
		items: NavItem[];
	};

	const aiNavItems: NavItem[] = [
		{ href: '/dashboard', label: 'Dashboard', icon: 'dashboard', variant: 'primary' },
		{ href: '/insights', label: 'Insights', icon: 'insights', variant: 'primary' },
		{ href: '/semantic-search', label: 'Ask Gemma', icon: 'ask', variant: 'primary' },
		{ href: '/compare', label: 'Compare', icon: 'compare', variant: 'primary' }
	];

	const trainingNavItems: NavItem[] = [
		{ href: '/diary', label: 'Diary', icon: 'diary', variant: 'secondary' },
		{ href: '/charts', label: 'Charts', icon: 'charts', variant: 'secondary' }
	];

	const mapNavItems: NavItem[] = [
		{ href: '/heatmap', label: 'Heatmap', icon: 'heatmap', variant: 'secondary' },
		{ href: '/routes', label: 'Routes', icon: 'routes', variant: 'secondary' }
	];

	const systemNavItems: NavItem[] = [
		{ href: '/settings', label: 'Settings', icon: 'settings', variant: 'secondary' },
		{ href: '/auth/login', label: 'Strava Connection', icon: 'auth', variant: 'secondary' },
		{ href: '/about', label: 'About / Documentation', icon: 'about', variant: 'secondary' }
	];

	const navSections: NavSection[] = [
		{ key: 'ai', label: 'AI', ariaLabel: 'AI features', items: aiNavItems },
		{ key: 'training', label: 'Training', ariaLabel: 'Training features', items: trainingNavItems },
		{ key: 'maps', label: 'Maps', ariaLabel: 'Maps features', items: mapNavItems },
		{ key: 'system', label: 'System', ariaLabel: 'System features', items: systemNavItems }
	];

	const pageLabels = [
		{ href: '/dashboard', label: 'Dashboard' },
		{ href: '/insights', label: 'Insights' },
		{ href: '/semantic-search', label: 'Ask Gemma' },
		{ href: '/compare', label: 'Compare' },
		{ href: '/diary', label: 'Diary' },
		{ href: '/charts', label: 'Charts' },
		{ href: '/heatmap', label: 'Heatmap' },
		{ href: '/routes', label: 'Routes' },
		{ href: '/settings', label: 'Settings' },
		{ href: '/auth/login', label: 'Strava Connection' },
		{ href: '/auth/callback', label: 'Authentication' },
		{ href: '/about', label: 'About / Documentation' }
	];

	let currentPathname = '/';
	let mobileSidebarOpen = false;
	let currentPageLabel = 'Dashboard';
	let currentUserLabel = 'Anonymous';
	let previousPathname = currentPathname;

	$: currentPathname = $page.url.pathname;
	$: currentPageLabel = getPageLabel(currentPathname);
	$: currentUserLabel = getSessionDisplayName($session);
	$: if (currentPathname !== previousPathname) {
		mobileSidebarOpen = false;
		previousPathname = currentPathname;
	}

	function getPageLabel(pathnameToCheck: string) {
		if (pathnameToCheck === '/') {
			return 'Dashboard';
		}

		const matchedLabel = pageLabels.find((item) => pathnameToCheck === item.href || pathnameToCheck.startsWith(`${item.href}/`));
		return matchedLabel?.label ?? 'Dashboard';
	}

	function openMobileSidebar() {
		mobileSidebarOpen = true;
	}

	function closeMobileSidebar() {
		mobileSidebarOpen = false;
	}

	function toggleMobileSidebar() {
		mobileSidebarOpen = !mobileSidebarOpen;
	}
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="color-scheme" content="light dark" />
		<meta name="description" content="A local Strava training diary with AI summaries, Gemma prompts, and route analysis." />
</svelte:head>

<div class="app-shell">
	<header class="app-shell__header">
		<div class="app-header__brandRow">
			<button
				type="button"
				class="mobile-toggle"
				aria-label={mobileSidebarOpen ? 'Close navigation menu' : 'Open navigation menu'}
				aria-expanded={mobileSidebarOpen}
				on:click={toggleMobileSidebar}
			>
				☰
			</button>

			<a class="app-brand" href="/dashboard" aria-label="Go to dashboard">
				<div class="app-brand__mark">S</div>
				<div>
					<p class="app-brand__eyebrow">Local Training Diary</p>
					<p class="app-brand__title">{title}</p>
				</div>
			</a>
		</div>

		<div class="app-header__page">
			<p class="app-header__eyebrow">Current section</p>
			<h1 class="app-header__title">{currentPageLabel}</h1>
		</div>

		<div class="app-header__user">
			<p class="app-header__eyebrow">Logged in user</p>
			<p class="app-header__userName">{currentUserLabel}</p>
		</div>
	</header>

	<div class="app-shell__workspace">
		<button
			type="button"
			class={`app-sidebar-backdrop ${mobileSidebarOpen ? 'is-open' : ''}`}
			aria-label="Close navigation menu"
			on:click={closeMobileSidebar}
		></button>

		<nav class={`app-sidebar ${mobileSidebarOpen ? 'is-open' : ''}`} aria-label="Primary navigation">
			<div class="app-sidebar__panel">
				<div class="app-sidebar__hint">
					<span class="app-sidebar__hint-icon" aria-hidden="true">☰</span>
					<span class="app-sidebar__label">Menu</span>
				</div>

				<div class="app-sidebar__sections">
					{#each navSections as section}
						<section class={`app-sidebar__group ${section.key === 'system' ? 'mt-auto' : ''}`} aria-label={section.ariaLabel}>
							<p class="app-sidebar__group-label">{section.label}</p>
							<div class="app-sidebar__group-items">
								{#each section.items as item}
									<NavLink href={item.href} label={item.label} icon={item.icon} variant={item.variant} active={$page.url.pathname === item.href || $page.url.pathname.startsWith(`${item.href}/`)} />
								{/each}
							</div>
						</section>
					{/each}
				</div>
			</div>
		</nav>

		<main class="app-shell__content">
			<slot />
		</main>
	</div>
</div>
