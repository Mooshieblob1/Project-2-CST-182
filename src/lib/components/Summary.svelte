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

	// Update calculations to use filtered transactions
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

	// Calculate monthly breakdown
	let monthlyData = $derived(() => {
		const monthlyTotals: Record<string, { income: number; expenses: number; balance: number }> = {};

		transactions.forEach((t) => {
			const monthKey = new Date(t.date).toLocaleDateString('en-US', {
				year: 'numeric',
				month: 'short'
			});
			if (!monthlyTotals[monthKey]) {
				monthlyTotals[monthKey] = { income: 0, expenses: 0, balance: 0 };
			}

			if (t.type === 'income') {
				monthlyTotals[monthKey].income += t.amount;
			} else {
				monthlyTotals[monthKey].expenses += t.amount;
			}
			monthlyTotals[monthKey].balance =
				monthlyTotals[monthKey].income - monthlyTotals[monthKey].expenses;
		});

		return Object.entries(monthlyTotals)
			.map(([month, data]) => ({ month, ...data }))
			.sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime());
	});

	// Calculate spending trends
	let spendingTrends = $derived(() => {
		const last30Days = transactions.filter((t) => {
			const transactionDate = new Date(t.date);
			const thirtyDaysAgo = new Date();
			thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
			return transactionDate >= thirtyDaysAgo;
		});

		const last7Days = transactions.filter((t) => {
			const transactionDate = new Date(t.date);
			const sevenDaysAgo = new Date();
			sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
			return transactionDate >= sevenDaysAgo;
		});

		return {
			last7DaysExpenses: last7Days
				.filter((t) => t.type === 'expense')
				.reduce((sum, t) => sum + t.amount, 0),
			last30DaysExpenses: last30Days
				.filter((t) => t.type === 'expense')
				.reduce((sum, t) => sum + t.amount, 0),
			last7DaysIncome: last7Days
				.filter((t) => t.type === 'income')
				.reduce((sum, t) => sum + t.amount, 0),
			last30DaysIncome: last30Days
				.filter((t) => t.type === 'income')
				.reduce((sum, t) => sum + t.amount, 0)
		};
	});

	// Calculate average transaction amounts
	let averages = $derived(() => {
		const incomeTransactions = transactions.filter((t) => t.type === 'income');
		const expenseTransactions = transactions.filter((t) => t.type === 'expense');

		return {
			avgIncome:
				incomeTransactions.length > 0
					? incomeTransactions.reduce((sum, t) => sum + t.amount, 0) / incomeTransactions.length
					: 0,
			avgExpense:
				expenseTransactions.length > 0
					? expenseTransactions.reduce((sum, t) => sum + t.amount, 0) / expenseTransactions.length
					: 0
		};
	});

	// Find largest transactions
	let extremeTransactions = $derived(() => {
		const incomeTransactions = transactions.filter((t) => t.type === 'income');
		const expenseTransactions = transactions.filter((t) => t.type === 'expense');

		return {
			largestIncome:
				incomeTransactions.length > 0
					? incomeTransactions.reduce((max, t) => (t.amount > max.amount ? t : max))
					: null,
			largestExpense:
				expenseTransactions.length > 0
					? expenseTransactions.reduce((max, t) => (t.amount > max.amount ? t : max))
					: null
		};
	});

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

	// Recalculate summary based on filtered transactions
	let filteredSummary = $derived(() => {
		const filtered = filteredTransactions();
		const income = filtered
			.filter((t: Transaction) => t.type === 'income')
			.reduce((sum: number, t: Transaction) => sum + t.amount, 0);

		const expenses = filtered
			.filter((t: Transaction) => t.type === 'expense')
			.reduce((sum: number, t: Transaction) => sum + t.amount, 0);

		const balance = income - expenses;

		return { income, expenses, balance };
	});
</script>

<div class="space-y-6">
	<!-- Time Range Filter -->
	<div class="rounded-lg bg-white p-4 shadow-lg">
		<h3 class="mb-3 text-lg font-semibold text-gray-800">Time Range</h3>
		<div class="flex flex-wrap gap-2">
			<button
				onclick={() => (selectedTimeRange = 'all')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'all'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
			>
				All Time
			</button>
			<button
				onclick={() => (selectedTimeRange = 'week')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'week'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
			>
				Last 7 Days
			</button>
			<button
				onclick={() => (selectedTimeRange = 'month')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'month'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
			>
				Last 30 Days
			</button>
			<button
				onclick={() => (selectedTimeRange = 'quarter')}
				class={`rounded-md px-4 py-2 font-medium transition-colors ${
					selectedTimeRange === 'quarter'
						? 'bg-blue-500 text-white'
						: 'bg-gray-100 text-gray-700 hover:bg-gray-200'
				}`}
			>
				Last 90 Days
			</button>
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
					<p class="text-2xl font-bold text-green-600">
						{formatCurrency(filteredSummary().income)}
					</p>
					{#if selectedTimeRange !== 'all'}
						<p class="text-xs text-gray-500">
							{filteredTransactions().filter((t) => t.type === 'income').length} transactions
						</p>
					{/if}
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
					<p class="text-2xl font-bold text-red-600">
						{formatCurrency(filteredSummary().expenses)}
					</p>
					{#if selectedTimeRange !== 'all'}
						<p class="text-xs text-gray-500">
							{filteredTransactions().filter((t) => t.type === 'expense').length} transactions
						</p>
					{/if}
				</div>
			</div>
		</div>

		<!-- Balance -->
		<div
			class={`rounded-lg border-l-4 bg-white p-6 shadow-lg ${filteredSummary().balance >= 0 ? 'border-blue-500' : 'border-yellow-500'}`}
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
					<p class="text-sm font-medium text-gray-600">Balance</p>
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
						{filteredSummary().expenses > 0
							? formatCurrency(filteredSummary().income / filteredSummary().expenses)
							: 'N/A'}
					</p>
					<p class="text-sm text-gray-600">Income/Expense Ratio</p>
				</div>
			</div>
		</div>
	{/if}

	<!-- Advanced Analytics -->
	{#if transactions.length > 0}
		<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
			<!-- Spending Trends -->
			<div class="rounded-lg bg-white p-6 shadow-lg">
				<h3 class="mb-4 text-lg font-semibold text-gray-800">Spending Trends</h3>
				<div class="space-y-4">
					<div class="flex items-center justify-between">
						<span class="text-gray-700">Last 7 Days</span>
						<div class="text-right">
							<p class="font-semibold text-red-600">
								{formatCurrency(spendingTrends().last7DaysExpenses)}
							</p>
							<p class="text-xs text-green-600">
								+{formatCurrency(spendingTrends().last7DaysIncome)} income
							</p>
						</div>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-gray-700">Last 30 Days</span>
						<div class="text-right">
							<p class="font-semibold text-red-600">
								{formatCurrency(spendingTrends().last30DaysExpenses)}
							</p>
							<p class="text-xs text-green-600">
								+{formatCurrency(spendingTrends().last30DaysIncome)} income
							</p>
						</div>
					</div>
					<div class="border-t pt-2">
						<div class="flex items-center justify-between">
							<span class="font-medium text-gray-700">Daily Average (30d)</span>
							<span class="font-semibold text-gray-800">
								{formatCurrency(spendingTrends().last30DaysExpenses / 30)}
							</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Transaction Averages -->
			<div class="rounded-lg bg-white p-6 shadow-lg">
				<h3 class="mb-4 text-lg font-semibold text-gray-800">Averages</h3>
				<div class="space-y-4">
					<div class="flex items-center justify-between">
						<span class="text-gray-700">Average Income</span>
						<span class="font-semibold text-green-600">{formatCurrency(averages().avgIncome)}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-gray-700">Average Expense</span>
						<span class="font-semibold text-red-600">{formatCurrency(averages().avgExpense)}</span>
					</div>
					{#if extremeTransactions().largestIncome}
						<div class="border-t pt-2">
							<p class="mb-1 text-sm text-gray-600">Largest Income</p>
							<p class="font-semibold text-green-600">
								{formatCurrency(extremeTransactions().largestIncome?.amount || 0)}
							</p>
							<p class="text-xs text-gray-500 capitalize">
								{extremeTransactions().largestIncome?.category} - {extremeTransactions()
									.largestIncome?.description}
							</p>
						</div>
					{/if}
					{#if extremeTransactions().largestExpense}
						<div class="border-t pt-2">
							<p class="mb-1 text-sm text-gray-600">Largest Expense</p>
							<p class="font-semibold text-red-600">
								{formatCurrency(extremeTransactions().largestExpense?.amount || 0)}
							</p>
							<p class="text-xs text-gray-500 capitalize">
								{extremeTransactions().largestExpense?.category} - {extremeTransactions()
									.largestExpense?.description}
							</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}

	<!-- Monthly Breakdown -->
	{#if monthlyData().length > 1}
		<div class="rounded-lg bg-white p-6 shadow-lg">
			<h3 class="mb-4 text-lg font-semibold text-gray-800">Monthly Breakdown</h3>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-gray-50">
						<tr>
							<th class="px-4 py-2 text-left font-medium text-gray-600">Month</th>
							<th class="px-4 py-2 text-right font-medium text-gray-600">Income</th>
							<th class="px-4 py-2 text-right font-medium text-gray-600">Expenses</th>
							<th class="px-4 py-2 text-right font-medium text-gray-600">Balance</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-gray-200">
						{#each monthlyData() as month}
							<tr class="hover:bg-gray-50">
								<td class="px-4 py-2 font-medium">{month.month}</td>
								<td class="px-4 py-2 text-right text-green-600">{formatCurrency(month.income)}</td>
								<td class="px-4 py-2 text-right text-red-600">{formatCurrency(month.expenses)}</td>
								<td
									class="px-4 py-2 text-right font-medium {month.balance >= 0
										? 'text-blue-600'
										: 'text-yellow-600'}"
								>
									{formatCurrency(month.balance)}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>
