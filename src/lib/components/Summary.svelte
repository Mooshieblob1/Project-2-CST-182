<script lang="ts">
	interface Transaction {
		id: string;
		type: 'income' | 'expense';
		amount: number;
		category: string;
		description: string;
		date: string;
	}

	interface Props {
		transactions: Transaction[];
	}

	let { transactions }: Props = $props();

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}

	let selectedTimeRange = $state('all');

	// Filter transactions based on time range
	let filteredTransactions = $derived(() => {
		const now = new Date();
		switch (selectedTimeRange) {
			case 'week':
				const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
				return transactions.filter((t) => new Date(t.date) >= weekAgo);
			case 'month':
				const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
				return transactions.filter((t) => new Date(t.date) >= monthAgo);
			case 'quarter':
				const quarterAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
				return transactions.filter((t) => new Date(t.date) >= quarterAgo);
			default:
				return transactions;
		}
	});

	// Calculate filtered summary
	let filteredSummary = $derived(() => {
		const filtered = filteredTransactions();
		const income = filtered
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);
		const expenses = filtered
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);
		const balance = income - expenses;

		return { income, expenses, balance };
	});

	// Category breakdowns
	let incomeByCategory = $derived(() => {
		const categoryTotals = new Map<string, number>();
		filteredTransactions()
			.filter((t) => t.type === 'income')
			.forEach((t) => {
				const current = categoryTotals.get(t.category) || 0;
				categoryTotals.set(t.category, current + t.amount);
			});

		return Array.from(categoryTotals.entries())
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	let expensesByCategory = $derived(() => {
		const categoryTotals = new Map<string, number>();
		filteredTransactions()
			.filter((t) => t.type === 'expense')
			.forEach((t) => {
				const current = categoryTotals.get(t.category) || 0;
				categoryTotals.set(t.category, current + t.amount);
			});

		return Array.from(categoryTotals.entries())
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});
</script>

<div class="space-y-6">
	<!-- Time Range Filter -->
	<div class="rounded-lg bg-white p-4 shadow-lg dark:bg-gray-800">
		<h3 class="mb-3 text-lg font-semibold text-gray-800 dark:text-white">Time Range</h3>
		<div class="flex flex-wrap gap-2">
			<button
				onclick={() => (selectedTimeRange = 'all')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'all'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
				}`}
			>
				All Time
			</button>
			<button
				onclick={() => (selectedTimeRange = 'week')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'week'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
				}`}
			>
				Last 7 Days
			</button>
			<button
				onclick={() => (selectedTimeRange = 'month')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'month'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
				}`}
			>
				Last 30 Days
			</button>
			<button
				onclick={() => (selectedTimeRange = 'quarter')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'quarter'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
				}`}
			>
				Last 90 Days
			</button>
		</div>
	</div>

	<!-- Financial Overview Cards -->
	<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
		<!-- Total Income -->
		<div class="rounded-lg border-l-4 border-green-500 bg-white p-6 shadow-lg dark:bg-gray-800">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 6v6m0 0v6m0-6h6m-6 0H6"
						></path>
					</svg>
				</div>
				<div class="ml-4">
					<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Income</p>
					<p class="text-2xl font-bold text-green-600">
						{formatCurrency(filteredSummary().income)}
					</p>
					{#if selectedTimeRange !== 'all'}
						<p class="text-xs text-gray-500 dark:text-gray-400">
							{filteredTransactions().filter((t) => t.type === 'income').length} transactions
						</p>
					{/if}
				</div>
			</div>
		</div>

		<!-- Total Expenses -->
		<div class="rounded-lg border-l-4 border-red-500 bg-white p-6 shadow-lg dark:bg-gray-800">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"
						></path>
					</svg>
				</div>
				<div class="ml-4">
					<p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Expenses</p>
					<p class="text-2xl font-bold text-red-600">
						{formatCurrency(filteredSummary().expenses)}
					</p>
					{#if selectedTimeRange !== 'all'}
						<p class="text-xs text-gray-500 dark:text-gray-400">
							{filteredTransactions().filter((t) => t.type === 'expense').length} transactions
						</p>
					{/if}
				</div>
			</div>
		</div>

		<!-- Balance -->
		<div
			class={`rounded-lg border-l-4 bg-white p-6 shadow-lg dark:bg-gray-800 ${filteredSummary().balance >= 0 ? 'border-blue-500' : 'border-yellow-500'}`}
		>
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg
						class={`h-8 w-8 ${filteredSummary().balance >= 0 ? 'text-blue-500' : 'text-yellow-500'}`}
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
						></path>
					</svg>
				</div>
				<div class="ml-4">
					<p class="text-sm font-medium text-gray-600 dark:text-gray-300">Balance</p>
					<p
						class={`text-2xl font-bold ${filteredSummary().balance >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}
					>
						{formatCurrency(filteredSummary().balance)}
					</p>
					{#if selectedTimeRange !== 'all'}
						<p class="text-xs text-gray-500">
							{filteredTransactions().length} total transactions
						</p>
					{/if}
				</div>
			</div>
		</div>
	</div>

	<!-- Category Breakdowns -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<!-- Income by Category -->
		<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
			<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800 dark:text-white">
				<svg
					class="mr-2 h-5 w-5 text-green-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 6v6m0 0v6m0-6h6m-6 0H6"
					></path>
				</svg>
				Income by Category
			</h3>
			{#if incomeByCategory().length > 0}
				<div class="space-y-3">
					{#each incomeByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<div class="mr-3 h-4 w-4 rounded bg-green-400"></div>
								<span class="text-sm font-medium text-gray-700 capitalize">{category}</span>
							</div>
							<div class="text-right">
								<div class="text-sm font-bold text-green-600">
									{formatCurrency(amount)}
								</div>
								<div class="text-xs text-gray-500">
									{filteredSummary().income > 0
										? Math.round((amount / filteredSummary().income) * 100)
										: 0}%
								</div>
							</div>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-green-400"
								style="width: {filteredSummary().income > 0
									? (amount / filteredSummary().income) * 100
									: 0}%"
							></div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="py-4 text-center text-gray-500">No income data available</p>
			{/if}
		</div>

		<!-- Expenses by Category -->
		<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
			<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800 dark:text-white">
				<svg
					class="mr-2 h-5 w-5 text-red-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
				</svg>
				Expenses by Category
			</h3>
			{#if expensesByCategory().length > 0}
				<div class="space-y-3">
					{#each expensesByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<div class="flex items-center">
								<div class="mr-3 h-4 w-4 rounded bg-red-400"></div>
								<span class="text-sm font-medium text-gray-700 capitalize">{category}</span>
							</div>
							<div class="text-right">
								<div class="text-sm font-bold text-red-600">
									{formatCurrency(amount)}
								</div>
								<div class="text-xs text-gray-500">
									{filteredSummary().expenses > 0
										? Math.round((amount / filteredSummary().expenses) * 100)
										: 0}%
								</div>
							</div>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-red-400"
								style="width: {filteredSummary().expenses > 0
									? (amount / filteredSummary().expenses) * 100
									: 0}%"
							></div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="py-4 text-center text-gray-500">No expense data available</p>
			{/if}
		</div>
	</div>

	<!-- Quick Stats -->
	{#if transactions.length > 0}
		<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
			<h3 class="mb-4 text-lg font-semibold text-gray-800 dark:text-white">Quick Stats</h3>
			<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
				<div class="text-center">
					<p class="text-2xl font-bold text-blue-600">{filteredTransactions().length}</p>
					<p class="text-sm text-gray-600 dark:text-gray-300">Transactions</p>
				</div>
				<div class="text-center">
					<p class="text-2xl font-bold text-green-600">
						{filteredTransactions().filter((t) => t.type === 'income').length}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-300">Income</p>
				</div>
				<div class="text-center">
					<p class="text-2xl font-bold text-red-600">
						{filteredTransactions().filter((t) => t.type === 'expense').length}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-300">Expenses</p>
				</div>
				<div class="text-center">
					<p class="text-2xl font-bold text-purple-600">
						{filteredSummary().expenses > 0
							? (filteredSummary().income / filteredSummary().expenses).toFixed(2)
							: '∞'}
					</p>
					<p class="text-sm text-gray-600 dark:text-gray-300">Income/Expense Ratio</p>
				</div>
			</div>
		</div>
	{/if}
</div>
