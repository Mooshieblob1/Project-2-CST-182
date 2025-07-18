<script lang="ts">
	import { themeStore } from '$lib/stores/theme';
	import { onMount } from 'svelte';

	let theme = $derived($themeStore);

	onMount(() => {
		themeStore.init();
	});

	function handleToggle() {
		themeStore.toggle();
	}
</script>

<div class="flex items-center space-x-3">
	<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
		{theme === 'light' ? '☀️' : '🌙'}
	</span>
	<button
		onclick={handleToggle}
		class="relative inline-flex h-8 w-14 items-center rounded-full bg-gray-200 shadow-md transition-colors hover:bg-gray-300 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none dark:bg-gray-700 dark:hover:bg-gray-600"
		title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
		aria-label={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
	>
		<span
			class={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform duration-200 ease-in-out dark:bg-gray-200 ${
				theme === 'dark' ? 'translate-x-7' : 'translate-x-1'
			}`}
		>
			{#if theme === 'light'}
				<!-- Sun icon -->
				<svg
					class="h-6 w-6 p-1 text-yellow-500"
					fill="currentColor"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						fill-rule="evenodd"
						d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
						clip-rule="evenodd"
					></path>
				</svg>
			{:else}
				<!-- Moon icon -->
				<svg
					class="h-6 w-6 p-1 text-gray-600"
					fill="currentColor"
					viewBox="0 0 20 20"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
				</svg>
			{/if}
		</span>
	</button>
	<span class="text-sm font-medium text-gray-700 dark:text-gray-300">
		{theme === 'light' ? 'Light' : 'Dark'}
	</span>
</div>
