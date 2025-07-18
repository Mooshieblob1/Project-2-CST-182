import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark';

// Create a writable store for theme state
function createThemeStore() {
	const { subscribe, set, update } = writable<Theme>('light');

	return {
		subscribe,
		toggle: () =>
			update((theme) => {
				const newTheme: Theme = theme === 'light' ? 'dark' : 'light';
				if (browser) {
					localStorage.setItem('theme', newTheme);
					updateDocumentClass(newTheme);
					console.log(`Theme switched to: ${newTheme}`);
				}
				return newTheme;
			}),
		set: (theme: Theme) => {
			if (browser) {
				localStorage.setItem('theme', theme);
				updateDocumentClass(theme);
				console.log(`Theme set to: ${theme}`);
			}
			set(theme);
		},
		init: () => {
			if (browser) {
				// Check for saved theme preference or default to light
				const savedTheme = localStorage.getItem('theme') as Theme | null;
				const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
				const initialTheme: Theme = savedTheme || (prefersDark ? 'dark' : 'light');

				console.log(`Initializing theme: ${initialTheme}`);
				updateDocumentClass(initialTheme);
				set(initialTheme);

				// Listen for system theme changes
				const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
				mediaQuery.addEventListener('change', (e) => {
					if (!localStorage.getItem('theme')) {
						const systemTheme: Theme = e.matches ? 'dark' : 'light';
						updateDocumentClass(systemTheme);
						set(systemTheme);
					}
				});
			}
		}
	};
}

function updateDocumentClass(theme: Theme) {
	if (browser && document.documentElement) {
		console.log(
			`Updating document class for theme: ${theme}, current classes:`,
			document.documentElement.className
		);

		// For Tailwind CSS dark mode, we only need to add/remove the 'dark' class
		// Light mode is the default when 'dark' class is absent
		if (theme === 'dark') {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}

		// Force a style recalculation
		document.documentElement.style.colorScheme = theme;

		console.log(`Document class updated, new classes:`, document.documentElement.className);

		// Force a repaint by temporarily changing and restoring a style
		const body = document.body;
		const originalTransition = body.style.transition;
		body.style.transition = 'none';
		void body.offsetHeight; // Trigger reflow
		body.style.transition = originalTransition;
	}
}

export const themeStore = createThemeStore();
