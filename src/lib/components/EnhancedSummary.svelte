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

	// Date filter options
	let dateFilter = $state('all');
	let customStartDate = $state('');
	let customEndDate = $state('');

	// Filtered transactions based on date
	let filteredTransactions = $derived.by(() => {
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
	let summary = $derived.by(() => {
		const income = filteredTransactions
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);

		const expenses = filteredTransactions
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);

		const balance = income - expenses;

		return { income, expenses, balance };
	});

	// Calculate expense breakdown by category
	let expenseByCategory = $derived.by(() => {
		const categoryTotals: Record<string, number> = {};

		filteredTransactions
			.filter((t) => t.type === 'expense')
			.forEach((t) => {
				categoryTotals[t.category] = (categoryTotals[t.category] || 0) + t.amount;
			});

		return Object.entries(categoryTotals)
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	// Calculate income breakdown by category
	let incomeByCategory = $derived.by(() => {
		const categoryTotals: Record<string, number> = {};

		filteredTransactions
			.filter((t) => t.type === 'income')
			.forEach((t) => {
				categoryTotals[t.category] = (categoryTotals[t.category] || 0) + t.amount;
			});

		return Object.entries(categoryTotals)
			.map(([category, amount]) => ({ category, amount }))
			.sort((a, b) => b.amount - a.amount);
	});

	function createChartData(data: { category: string; amount: number }[]) {
		return data.map((d) => ({ name: d.category, value: d.amount }));
	}

	let incomeChartData = $derived(createChartData(incomeByCategory));
	let expenseChartData = $derived(createChartData(expenseByCategory));

	const colors = [
		'#34D399',
		'#60A5FA',
		'#FBBF24',
		'#F87171',
		'#A78BFA',
		'#F472B6',
		'#4ADE80',
		'#2DD4BF',
		'#a855f7',
		'#ec4899'
	];

	function calculateOffsets(data: { name: string; value: number }[]) {
		const total = data.reduce((sum, d) => sum + d.value, 0);
		if (total === 0) return data.map(() => ({ percentage: 0, dasharray: '0 100', offset: 0 }));

		let offset = 0;
		return data.map((d) => {
			const percentage = (d.value / total) * 100;
			const dasharray = `${percentage} ${100 - percentage}`;
			const currentOffset = offset;
			offset += percentage;
			return { percentage, dasharray, offset: currentOffset };
		});
	}

	let incomeOffsets = $derived(calculateOffsets(incomeChartData));
	let expenseOffsets = $derived(calculateOffsets(expenseChartData));

	function formatCurrency(value: number) {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(value);
	}

	let timeSeriesData = $derived.by(() => {
		const series: Record<string, { date: string; income: number; expenses: number }> = {};

		filteredTransactions.forEach((t) => {
			const date = t.date.split('T')[0];
			if (!series[date]) {
				series[date] = { date, income: 0, expenses: 0 };
			}
			if (t.type === 'income') {
				series[date].income += t.amount;
			} else {
				series[date].expenses += t.amount;
			}
		});

		return Object.values(series).sort(
			(a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
		);
	});
</script>

<div class="space-y-8 rounded-lg bg-gray-800 p-6 text-white shadow-lg">
	<h2 class="text-3xl font-bold">Financial Analytics</h2>

	<!-- Date Filter -->
	<div class="flex flex-wrap items-center gap-4 rounded-lg bg-gray-700 p-4">
		<select
			bind:value={dateFilter}
			class="rounded-lg border-gray-600 bg-gray-600 p-2 focus:border-blue-500 focus:ring-blue-500"
		>
			<option value="all">All Time</option>
			<option value="week">Last 7 Days</option>
			<option value="month">This Month</option>
			<option value="quarter">This Quarter</option>
			<option value="year">This Year</option>
			<option value="custom">Custom Range</option>
		</select>

		{#if dateFilter === 'custom'}
			<div class="flex items-center gap-2">
				<input
					type="date"
					bind:value={customStartDate}
					class="rounded-lg border-gray-500 bg-gray-600 p-2"
				/>
				<span>to</span>
				<input
					type="date"
					bind:value={customEndDate}
					class="rounded-lg border-gray-500 bg-gray-600 p-2"
				/>
			</div>
		{/if}
	</div>

	<!-- Key Metrics -->
	<div class="grid grid-cols-1 gap-6 md:grid-cols-3">
		<div class="rounded-lg bg-green-800 p-6">
			<p class="text-sm text-green-200">Total Income</p>
			<p class="text-3xl font-bold">{formatCurrency(summary.income)}</p>
		</div>
		<div class="rounded-lg bg-red-800 p-6">
			<p class="text-sm text-red-200">Total Expenses</p>
			<p class="text-3xl font-bold">{formatCurrency(summary.expenses)}</p>
		</div>
		<div class="rounded-lg bg-blue-800 p-6">
			<p class="text-sm text-blue-200">Net Balance</p>
			<p class="text-3xl font-bold">{formatCurrency(summary.balance)}</p>
		</div>
	</div>

	<!-- Charts -->
	<div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
		<!-- Expense Breakdown -->
		<div class="rounded-lg bg-gray-700 p-6">
			<h3 class="mb-4 text-xl font-semibold">Expense Breakdown</h3>
			<div class="flex items-center">
				<div class="relative h-48 w-48">
					<!-- Donut Chart -->
					<svg viewBox="0 0 100 100" class="h-full w-full">
						{#if expenseChartData.length > 0}
							{#each expenseChartData as data, i}
								<circle
									cx="50"
									cy="50"
									r="45"
									fill="transparent"
									stroke-width="10"
									stroke={colors[i % colors.length]}
									stroke-dasharray={expenseOffsets[i].dasharray}
									stroke-dashoffset={-expenseOffsets[i].offset}
									transform="rotate(-90 50 50)"
								/>
							{/each}
						{/if}
					</svg>
					<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
						<p class="text-xs text-gray-400">Total Expenses</p>
						<p class="text-lg font-bold">{formatCurrency(summary.expenses)}</p>
					</div>
				</div>
				<div class="ml-6 flex-1">
					<!-- Legend -->
					<ul class="space-y-2">
						{#each expenseChartData as data, i}
							<li class="flex items-center">
								<span
									class="mr-2 inline-block h-3 w-3 rounded-full"
									style="background-color: {colors[i % colors.length]};"
								></span>
								<span>{data.name}: {formatCurrency(data.value)}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>
		</div>

		<!-- Income Breakdown -->
		<div class="rounded-lg bg-gray-700 p-6">
			<h3 class="mb-4 text-xl font-semibold">Income Breakdown</h3>
			<div class="flex items-center">
				<div class="relative h-48 w-48">
					<!-- Donut Chart -->
					<svg viewBox="0 0 100 100" class="h-full w-full">
						{#if incomeChartData.length > 0}
							{#each incomeChartData as data, i}
								<circle
									cx="50"
									cy="50"
									r="45"
									fill="transparent"
									stroke-width="10"
									stroke={colors[i % colors.length]}
									stroke-dasharray={incomeOffsets[i].dasharray}
									stroke-dashoffset={-incomeOffsets[i].offset}
									transform="rotate(-90 50 50)"
								/>
							{/each}
						{/if}
					</svg>
					<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
						<p class="text-xs text-gray-400">Total Income</p>
						<p class="text-lg font-bold">{formatCurrency(summary.income)}</p>
					</div>
				</div>
				<div class="ml-6 flex-1">
					<!-- Legend -->
					<ul class="space-y-2">
						{#each incomeChartData as data, i}
							<li class="flex items-center">
								<span
									class="mr-2 inline-block h-3 w-3 rounded-full"
									style="background-color: {colors[i % colors.length]};"
								></span>
								<span>{data.name}: {formatCurrency(data.value)}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>
		</div>
	</div>

	<!-- Income vs Expenses Line Chart -->
	<div class="rounded-lg bg-gray-700 p-6">
		<h3 class="mb-4 text-xl font-semibold">Income vs. Expenses Over Time</h3>
		<div class="h-64">
			<svg class="h-full w-full" preserveAspectRatio="xMidYMid meet" viewBox="0 0 500 250">
				{#if timeSeriesData.length > 0}
					{@const chartWidth = 500}
					{@const chartHeight = 250}
					{@const padding = { top: 20, right: 20, bottom: 30, left: 60 }}

					{@const xMax = chartWidth - padding.left - padding.right}
					{@const yMax = chartHeight - padding.top - padding.bottom}

					{@const data = timeSeriesData}
					{@const dates = data.map((d) => new Date(d.date))}
					{@const maxAmount = Math.max(
						1,
						...data.map((d) => d.income),
						...data.map((d) => d.expenses)
					)}

					{@const xScale = (date: Date) => {
						const timeRange = dates[dates.length - 1].getTime() - dates[0].getTime();
						if (timeRange === 0) return padding.left + xMax / 2;
						return padding.left + ((date.getTime() - dates[0].getTime()) / timeRange) * xMax;
					}}

					{@const yScale = (amount: number) => {
						if (maxAmount === 0) return chartHeight - padding.bottom;
						return chartHeight - padding.bottom - (amount / maxAmount) * yMax;
					}}

					<!-- Axes -->
					<g class="text-xs text-gray-400">
						<!-- Y-axis -->
						{#each Array(6) as _, i}
							{@const y = padding.top + (i * yMax) / 5}
							<line
								x1={padding.left}
								y1={y}
								x2={chartWidth - padding.right}
								y2={y}
								class="stroke-current text-gray-600"
								stroke-dasharray="2"
							/>
							<text x={padding.left - 8} y={y + 4} text-anchor="end" fill="currentColor">
								{formatCurrency(maxAmount * (1 - i / 5))}
							</text>
						{/each}
						<!-- X-axis -->
						<line
							x1={padding.left}
							y1={chartHeight - padding.bottom}
							x2={chartWidth - padding.right}
							y2={chartHeight - padding.bottom}
							class="stroke-current"
						/>
						{#if dates.length > 1}
							<text
								x={padding.left}
								y={chartHeight - padding.bottom + 15}
								text-anchor="start"
								fill="currentColor"
							>
								{dates[0].toLocaleDateString('en-us', { month: 'short', day: 'numeric' })}
							</text>
							<text
								x={chartWidth - padding.right}
								y={chartHeight - padding.bottom + 15}
								text-anchor="end"
								fill="currentColor"
							>
								{dates[dates.length - 1].toLocaleDateString('en-us', {
									month: 'short',
									day: 'numeric'
								})}
							</text>
						{/if}
					</g>

					<!-- Income Path -->
					{#if data.length > 1}
						<path
							d={`M ${data
								.map((d) => `${xScale(new Date(d.date))},${yScale(d.income)}`)
								.join(' L ')}`}
							fill="none"
							stroke="#34D399"
							stroke-width="2"
						/>
					{/if}

					<!-- Expense Path -->
					{#if data.length > 1}
						<path
							d={`M ${data
								.map((d) => `${xScale(new Date(d.date))},${yScale(d.expenses)}`)
								.join(' L ')}`}
							fill="none"
							stroke="#F87171"
							stroke-width="2"
						/>
					{/if}

					<!-- Data Points -->
					{#each data as d}
						<circle cx={xScale(new Date(d.date))} cy={yScale(d.income)} r="3" fill="#34D399" />
						<circle cx={xScale(new Date(d.date))} cy={yScale(d.expenses)} r="3" fill="#F87171" />
					{/each}
				{:else}
					<text
						x="250"
						y="125"
						text-anchor="middle"
						fill="currentColor"
						class="text-lg text-gray-500"
					>
						No data for this period
					</text>
				{/if}
			</svg>
		</div>
	</div>
</div>
