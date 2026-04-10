import { browser } from '$app/environment';
import { writable } from 'svelte/store';

const STORAGE_KEY = 'strava-training-diary-theme';

export type ThemeMode = 'light' | 'dark';

function getSystemTheme(): ThemeMode {
	if (!browser || !window.matchMedia('(prefers-color-scheme: dark)').matches) {
		return 'light';
	}

	return 'dark';
}

function readThemeFromStorage(): ThemeMode {
	if (!browser) {
		return 'light';
	}

	const storedTheme = localStorage.getItem(STORAGE_KEY);
	if (storedTheme === 'dark' || storedTheme === 'light') {
		return storedTheme;
	}

	return getSystemTheme();
}

function applyTheme(theme: ThemeMode) {
	if (!browser) {
		return;
	}

	document.documentElement.dataset.theme = theme;
	document.documentElement.style.colorScheme = theme;
}

function createThemeStore() {
	const { subscribe, set, update } = writable<ThemeMode>(readThemeFromStorage());

	if (browser) {
		subscribe((theme) => {
			localStorage.setItem(STORAGE_KEY, theme);
			applyTheme(theme);
		});
	}

	return {
		subscribe,
		setTheme(theme: ThemeMode) {
			set(theme);
		},
		toggleTheme() {
			update((current) => (current === 'dark' ? 'light' : 'dark'));
		}
	};
}

export const theme = createThemeStore();