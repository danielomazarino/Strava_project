// See https://svelte.dev/docs/kit/types#app.d.ts
declare global {
	namespace App {
		interface Locals {}
		interface PageData {
			apiBaseUrl?: string;
		}
		interface Platform {}
	}
}

export {};