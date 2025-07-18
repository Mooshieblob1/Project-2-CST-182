<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { themeStore } from '$lib/stores/theme';

	let { children } = $props();

	// Initialize theme on app load
	onMount(() => {
		console.log('Layout mounted, initializing theme...');
		themeStore.init();

		// Debug: check if dark class is applied
		setTimeout(() => {
			console.log('Current document classes:', document.documentElement.className);
			console.log('Current theme store value:', $themeStore);
		}, 100);
	});
</script>

{@render children()}
