import { browser } from '$app/environment';
import { dev } from '$app/environment';
import { env } from '$env/dynamic/public';
import { writable } from 'svelte/store';

const STORAGE_KEY = 'strava-training-diary-session';
export const DEMO_STRAVA_ATHLETE_ID = 14706324;

export type Session = {
	status: 'anonymous' | 'connected';
	userId: string;
	stravaAthleteId: number;
	connectedAt: string;
};

function readSessionFromStorage(): Session | null {
	if (!browser) {
		return null;
	}

	const rawSession = localStorage.getItem(STORAGE_KEY);
	if (!rawSession) {
		return null;
	}

	try {
		return JSON.parse(rawSession) as Session;
	} catch {
		return shouldUseDemoSession() ? createDemoSession() : null;
	}
}

function shouldUseDemoSession() {
	return dev && !env.PUBLIC_API_BASE_URL?.trim();
}

export function createDemoSession(stravaAthleteId = DEMO_STRAVA_ATHLETE_ID): Session {
	return {
		status: 'connected',
		userId: 'demo-user',
		stravaAthleteId,
		connectedAt: new Date().toISOString()
	};
}

export function getSessionDisplayName(currentSession: Session | null): string {
	if (!currentSession) {
		return 'Anonymous';
	}

	if (currentSession.userId === 'demo-user') {
		return `Demo user · ${currentSession.stravaAthleteId}`;
	}

	return `Athlete ${currentSession.stravaAthleteId}`;
}

function getInitialSession(): Session | null {
	const storedSession = readSessionFromStorage();
	if (storedSession) {
		return storedSession;
	}

	return browser && shouldUseDemoSession() ? createDemoSession() : null;
}

function createSessionStore() {
	const { subscribe, set } = writable<Session | null>(getInitialSession());

	if (browser) {
		subscribe((value) => {
			if (value === null) {
				localStorage.removeItem(STORAGE_KEY);
				return;
			}

			localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
		});
	}

	return {
		subscribe,
		setSession(value: Session) {
			set(value);
		},
		clearSession() {
			set(null);
		}
	};
}

export const session = createSessionStore();