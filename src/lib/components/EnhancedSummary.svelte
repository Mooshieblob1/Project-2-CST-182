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

	// Date filter options
	let dateFilter = $state('all');
	let customStartDate = $state('');
	let customEndDate = $state('');

	// Filtered transactions based on date
	let filteredTransactions = $derived(() => {
		if (dateFilter === 'all') return transactions;

		const now = new Date();
		let startDate: Date;
		let endDate = now;

		switch (dateFilter) {
			case 'week':
				startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
				break;
			case 'month':
				startDate = new Date(now.getFullYear(), now.getMonth(), 1);
				break;
			case 'quarter':
				const quarter = Math.floor(now.getMonth() / 3);
				startDate = new Date(now.getFullYear(), quarter * 3, 1);
				break;
			case 'year':
				startDate = new Date(now.getFullYear(), 0, 1);
				break;
			case 'custom':
				if (!customStartDate || !customEndDate) return transactions;
				startDate = new Date(customStartDate);
				endDate = new Date(customEndDate);
				endDate.setHours(23, 59, 59, 999); // End of day
				break;
			default:
				return transactions;
		}

		return transactions.filter((t) => {
			const transactionDate = new Date(t.date);
			return transactionDate >= startDate && transactionDate <= endDate;
		});
	});

	// Calculate financial summary
	let summary = $derived(() => {
		const income = filteredTransactions()
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);

		const expenses = filteredTransactions()
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);

		const balance = income - expenses;

		return { income, expenses, balance };
	});

	// Calculate expense breakdown by category
	let expenseByCategory = $derived(() => {
		const categoryTotals: Record<string, number> = {};

		filteredTransactions()
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

		filteredTransactions()
			.filter((t) => t.type === 'income')
			.forEach((t) => {
				categoryTotals[t.category] = (categoryTotals[t.category] || 0) + t.amount;
			});

		return Object.entries(categoryTotals)
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	// Monthly trends
	let monthlyTrends = $derived(() => {
		const monthlyData: Record<string, { income: number; expenses: number; balance: number }> = {};

		filteredTransactions().forEach((t) => {
			const date = new Date(t.date);
			const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

			if (!monthlyData[monthKey]) {
				monthlyData[monthKey] = { income: 0, expenses: 0, balance: 0 };
			}

			if (t.type === 'income') {
				monthlyData[monthKey].income += t.amount;
			} else {
				monthlyData[monthKey].expenses += t.amount;
			}
			monthlyData[monthKey].balance = monthlyData[monthKey].income - monthlyData[monthKey].expenses;
		});

		return Object.entries(monthlyData)
			.map(([month, data]) => ({ month, ...data }))
			.sort((a, b) => a.month.localeCompare(b.month))
			.slice(-6); // Last 6 months
	});

	// Spending insights
	let spendingInsights = $derived(() => {
		const expenses = filteredTransactions().filter((t) => t.type === 'expense');
		if (expenses.length === 0) return null;

		const totalExpenses = expenses.reduce((sum, t) => sum + t.amount, 0);
		const avgTransaction = totalExpenses / expenses.length;
		const largestExpense = Math.max(...expenses.map((t) => t.amount));
		const topCategory = expenseByCategory()[0];

		return {
			avgTransaction,
			largestExpense,
			topCategory: topCategory?.category || 'N/A',
			topCategoryAmount: topCategory?.amount || 0,
			topCategoryPercentage: topCategory ? (topCategory.amount / totalExpenses) * 100 : 0
		};
	});
</script>

<div class="space-y-6">
	<!-- Date Filter Controls -->
	<div class="rounded-lg bg-white p-6 shadow-lg">
		<h3 class="mb-4 text-lg font-semibold text-gray-800">Time Period</h3>
		<div class="mb-4 flex flex-wrap gap-3">
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'all'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'all')}
			>
				All Time
			</button>
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'week'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'week')}
			>
				Last 7 Days
			</button>
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'month'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'month')}
			>
				This Month
			</button>
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'quarter'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'quarter')}
			>
				This Quarter
			</button>
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'year'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'year')}
			>
				This Year
			</button>
			<button
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					dateFilter === 'custom'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
				onclick={() => (dateFilter = 'custom')}
			>
				Custom Range
			</button>
		</div>

		{#if dateFilter === 'custom'}
			<div class="flex items-center gap-4">
				<div>
					<label for="start-date" class="mb-1 block text-sm font-medium text-gray-700">From</label>
					<input
						id="start-date"
						type="date"
						bind:value={customStartDate}
						class="rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>
				<div>
					<label for="end-date" class="mb-1 block text-sm font-medium text-gray-700">To</label>
					<input
						id="end-date"
						type="date"
						bind:value={customEndDate}
						class="rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>
			</div>
		{/if}

		<div class="mt-2 text-sm text-gray-600">
			Showing {filteredTransactions().length} of {transactions.length} transactions
		</div>
	</div>

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

	<!-- Spending Insights -->
	{#if spendingInsights()}
		{@const insights = spendingInsights()}
		{#if insights}
			<div class="rounded-lg bg-white p-6 shadow-lg">
				<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800">
					<svg
						class="mr-2 h-5 w-5 text-purple-500"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
						></path>
					</svg>
					Spending Insights
				</h3>
				<div class="grid grid-cols-1 gap-4 md:grid-cols-4">
					<div class="rounded-lg bg-gray-50 p-4 text-center">
						<p class="text-2xl font-bold text-purple-600">
							{formatCurrency(insights.avgTransaction)}
						</p>
						<p class="text-sm text-gray-600">Avg Transaction</p>
					</div>
					<div class="rounded-lg bg-gray-50 p-4 text-center">
						<p class="text-2xl font-bold text-red-600">{formatCurrency(insights.largestExpense)}</p>
						<p class="text-sm text-gray-600">Largest Expense</p>
					</div>
					<div class="rounded-lg bg-gray-50 p-4 text-center">
						<p class="text-2xl font-bold text-orange-600 capitalize">{insights.topCategory}</p>
						<p class="text-sm text-gray-600">Top Category</p>
					</div>
					<div class="rounded-lg bg-gray-50 p-4 text-center">
						<p class="text-2xl font-bold text-indigo-600">
							{insights.topCategoryPercentage.toFixed(1)}%
						</p>
						<p class="text-sm text-gray-600">of Total Spending</p>
					</div>
				</div>
			</div>
		{/if}
	{/if}

	<!-- Monthly Trends -->
	{#if monthlyTrends().length > 1}
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 flex items-center text-lg font-semibold text-gray-800">
				<svg
					class="mr-2 h-5 w-5 text-blue-500"
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
				Monthly Trends (Last 6 Months)
			</h3>
			<div class="space-y-4">
				{#each monthlyTrends() as trend}
					<div class="border-l-4 border-gray-200 pl-4">
						<div class="mb-2 flex items-center justify-between">
							<h4 class="font-medium text-gray-800">
								{new Date(trend.month + '-01').toLocaleDateString('en-US', {
									year: 'numeric',
									month: 'long'
								})}
							</h4>
							<span class={`font-bold ${trend.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
								{formatCurrency(trend.balance)}
							</span>
						</div>
						<div class="grid grid-cols-2 gap-4 text-sm">
							<div>
								<span class="text-green-600">Income: {formatCurrency(trend.income)}</span>
							</div>
							<div>
								<span class="text-red-600">Expenses: {formatCurrency(trend.expenses)}</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}

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
			{#if incomeByCategory().length > 0}
				<div class="space-y-3">
					{#each incomeByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<span class="text-gray-700 capitalize">{category}</span>
							<span class="font-semibold text-green-600">{formatCurrency(amount)}</span>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-green-500"
								style="width: {summary().income > 0 ? (amount / summary().income) * 100 : 0}%"
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
			{#if expenseByCategory().length > 0}
				<div class="space-y-3">
					{#each expenseByCategory() as { category, amount }}
						<div class="flex items-center justify-between">
							<span class="text-gray-700 capitalize">{category}</span>
							<span class="font-semibold text-red-600">{formatCurrency(amount)}</span>
						</div>
						<div class="h-2 w-full rounded-full bg-gray-200">
							<div
								class="h-2 rounded-full bg-red-500"
								style="width: {summary().expenses > 0 ? (amount / summary().expenses) * 100 : 0}%"
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
	{#if filteredTransactions().length > 0}
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 text-lg font-semibold text-gray-800">Quick Stats</h3>
			<div class="grid grid-cols-2 gap-4 text-center md:grid-cols-4">
				<div>
					<p class="text-2xl font-bold text-blue-600">{filteredTransactions().length}</p>
					<p class="text-sm text-gray-600">Total Transactions</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-green-600">
						{filteredTransactions().filter((t) => t.type === 'income').length}
					</p>
					<p class="text-sm text-gray-600">Income Entries</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-red-600">
						{filteredTransactions().filter((t) => t.type === 'expense').length}
					</p>
					<p class="text-sm text-gray-600">Expense Entries</p>
				</div>
				<div>
					<p class="text-2xl font-bold text-gray-600">
						{summary().expenses > 0 ? (summary().income / summary().expenses).toFixed(2) : 'N/A'}
					</p>
					<p class="text-sm text-gray-600">Income/Expense Ratio</p>
				</div>
			</div>
		</div>
	{/if}
</div>
