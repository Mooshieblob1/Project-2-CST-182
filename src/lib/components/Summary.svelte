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

	// Calculate financial summary
	let summary = $derived(() => {
		const income = transactions
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);

		const expenses = transactions
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);

		const balance = income - expenses;

		return { income, expenses, balance };
	});

	// Calculate expense breakdown by category
	let expenseByCategory = $derived(() => {
		const categoryTotals: Record<string, number> = {};

		transactions
			.filter((t) => t.type === 'expense')
			.forEach((t) => {
				categoryTotals[t.category] = (categoryTotals[t.category] || 0) + t.amount;
			});

		return Object.entries(categoryTotals)
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	// Calculate income breakdown by category
	let incomeByCategory = $derived(() => {
		const categoryTotals: Record<string, number> = {};

		transactions
			.filter((t) => t.type === 'income')
			.forEach((t) => {
				categoryTotals[t.category] = (categoryTotals[t.category] || 0) + t.amount;
			});

		return Object.entries(categoryTotals)
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}
</script>

<div class="space-y-6">
	<!-- Financial Overview Cards -->
	<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
		<!-- Total Income -->
		<div class="rounded-lg border-l-4 border-green-500 bg-white p-6 shadow-lg">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
						></path>
					</svg>
				</div>
				<div class="ml-4">
					<p class="text-sm font-medium text-gray-600">Total Income</p>
					<p class="text-2xl font-bold text-green-600">{formatCurrency(summary().income)}</p>
				</div>
			</div>
		</div>

		<!-- Total Expenses -->
		<div class="rounded-lg border-l-4 border-red-500 bg-white p-6 shadow-lg">
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"
						></path>
					</svg>
				</div>
				<div class="ml-4">
					<p class="text-sm font-medium text-gray-600">Total Expenses</p>
					<p class="text-2xl font-bold text-red-600">{formatCurrency(summary().expenses)}</p>
				</div>
			</div>
		</div>

		<!-- Balance -->
		<div
			class={`rounded-lg border-l-4 bg-white p-6 shadow-lg ${summary().balance >= 0 ? 'border-blue-500' : 'border-yellow-500'}`}
		>
			<div class="flex items-center">
				<div class="flex-shrink-0">
					<svg
						class={`h-8 w-8 ${summary().balance >= 0 ? 'text-blue-500' : 'text-yellow-500'}`}
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
					<p class="text-sm font-medium text-gray-600">Balance</p>
					<p
						class={`text-2xl font-bold ${summary().balance >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}
					>
						{formatCurrency(summary().balance)}
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Category Breakdowns -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<!-- Income by Category -->
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800">
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
						d="M7 11l5-5m0 0l5 5m-5-5v12"
					></path>
				</svg>
				Income by Category
			</h3>
			{#if incomeByCategory.length > 0}
				<div class="space-y-3">
					{#each incomeByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<span class="text-gray-700 capitalize">{category}</span>
							<span class="font-semibold text-green-600">{formatCurrency(amount)}</span>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-green-500"
								style="width: {(amount / summary().income) * 100}%"
							></div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="py-4 text-center text-gray-500">No income data available</p>
			{/if}
		</div>

		<!-- Expenses by Category -->
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800">
				<svg
					class="mr-2 h-5 w-5 text-red-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M17 13l-5 5m0 0l-5-5m5 5V6"
					></path>
				</svg>
				Expenses by Category
			</h3>
			{#if expenseByCategory.length > 0}
				<div class="space-y-3">
					{#each expenseByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<span class="text-gray-700 capitalize">{category}</span>
							<span class="font-semibold text-red-600">{formatCurrency(amount)}</span>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-red-500"
								style="width: {(amount / summary().expenses) * 100}%"
							></div>
						</div>
					{/each}
				</div>
			{:else}
				<p class="py-4 text-center text-gray-500">No expense data available</p>
			{/if}
		</div>
	</div>

	<!-- Monthly Summary (if we have transactions from multiple months) -->
	{#if transactions.length > 0}
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 text-lg font-semibold text-gray-800">Quick Stats</h3>
			<div class="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
				<div>
					<p class="text-2xl font-bold text-blue-600">{transactions.length}</p>
					<p class="text-sm text-gray-600">Total Transactions</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-green-600">
						{transactions.filter((t) => t.type === 'income').length}
					</p>
					<p class="text-sm text-gray-600">Income Entries</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-red-600">
						{transactions.filter((t) => t.type === 'expense').length}
					</p>
					<p class="text-sm text-gray-600">Expense Entries</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-gray-600">
						{summary().expenses > 0 ? formatCurrency(summary().income / summary().expenses) : 'N/A'}
					</p>
					<p class="text-sm text-gray-600">Income/Expense Ratio</p>
				</div>
			</div>
		</div>
	{/if}
</div>
