<script lang="ts">
	import { transactionStore } from '$lib';

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

	let sortBy = $state('date');
	let sortOrder = $state('desc');
	let filterType = $state('all');
	let searchTerm = $state('');
	let categoryFilter = $state('all');
	let amountMin = $state('');
	let amountMax = $state('');
	let dateFrom = $state('');
	let dateTo = $state('');
	let showAdvancedFilters = $state(false);

	// Get unique categories for filter dropdown
	let availableCategories = $derived(() => {
		const categories = new Set<string>();
		transactions.forEach((t) => categories.add(t.category));
		return Array.from(categories).sort();
	});

	// Enhanced filtered and sorted transactions
	let filteredTransactions = $derived(() => {
		let filtered = transactions;

		// Filter by type
		if (filterType !== 'all') {
			filtered = filtered.filter((t) => t.type === filterType);
		}

		// Filter by category
		if (categoryFilter !== 'all') {
			filtered = filtered.filter((t) => t.category === categoryFilter);
		}

		// Search filter
		if (searchTerm.trim()) {
			const search = searchTerm.toLowerCase();
			filtered = filtered.filter(
				(t) =>
					t.description.toLowerCase().includes(search) || t.category.toLowerCase().includes(search)
			);
		}

		// Amount range filter
		if (amountMin || amountMax) {
			const min = amountMin ? parseFloat(amountMin) : 0;
			const max = amountMax ? parseFloat(amountMax) : Infinity;
			filtered = filtered.filter((t) => t.amount >= min && t.amount <= max);
		}

		// Date range filter
		if (dateFrom || dateTo) {
			const fromDate = dateFrom ? new Date(dateFrom) : new Date('1900-01-01');
			const toDate = dateTo ? new Date(dateTo) : new Date('2100-01-01');
			toDate.setHours(23, 59, 59, 999); // End of day

			filtered = filtered.filter((t) => {
				const transactionDate = new Date(t.date);
				return transactionDate >= fromDate && transactionDate <= toDate;
			});
		}

		// Sort
		return filtered.sort((a, b) => {
			let aVal: string | number = a[sortBy as keyof Transaction];
			let bVal: string | number = b[sortBy as keyof Transaction];

			if (sortBy === 'amount') {
				aVal = Number(aVal);
				bVal = Number(bVal);
			}

			if (sortOrder === 'asc') {
				return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
			} else {
				return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
			}
		});
	});

	// Summary of filtered transactions
	let filteredSummary = $derived(() => {
		const income = filteredTransactions()
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);
		const expenses = filteredTransactions()
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);
		return { income, expenses, balance: income - expenses };
	});

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD'
		}).format(amount);
	}

	function formatDate(dateString: string): string {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function deleteTransaction(id: string) {
		if (confirm('Are you sure you want to delete this transaction?')) {
			transactionStore.removeTransaction(id);
		}
	}

	function clearAllTransactions() {
		if (confirm('Are you sure you want to delete ALL transactions? This cannot be undone.')) {
			transactionStore.clearAll();
		}
	}

	function exportFilteredData() {
		if (filteredTransactions().length === 0) {
			alert('No transactions to export');
			return;
		}

		// Create CSV content
		const headers = ['Date', 'Type', 'Amount', 'Category', 'Description'];
		const csvContent = [
			headers.join(','),
			...filteredTransactions().map((t) =>
				[t.date, t.type, t.amount, t.category, `"${t.description}"`].join(',')
			)
		].join('\n');

		// Create and download file
		const blob = new Blob([csvContent], { type: 'text/csv' });
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `filtered_transactions_${new Date().toISOString().split('T')[0]}.csv`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		window.URL.revokeObjectURL(url);
	}

	function clearAllFilters() {
		filterType = 'all';
		categoryFilter = 'all';
		searchTerm = '';
		amountMin = '';
		amountMax = '';
		dateFrom = '';
		dateTo = '';
	}

	function toggleAdvancedFilters() {
		showAdvancedFilters = !showAdvancedFilters;
		if (!showAdvancedFilters) {
			// Clear advanced filters when hiding
			categoryFilter = 'all';
			amountMin = '';
			amountMax = '';
			dateFrom = '';
			dateTo = '';
		}
	}
</script>

<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
	<!-- Header with Summary -->
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h2 class="text-2xl font-bold text-gray-800 dark:text-white">All Transactions</h2>
			<div class="mt-2 flex gap-4 text-sm">
				<span class="text-green-600">Income: {formatCurrency(filteredSummary().income)}</span>
				<span class="text-red-600">Expenses: {formatCurrency(filteredSummary().expenses)}</span>
				<span
					class={`font-semibold ${filteredSummary().balance >= 0 ? 'text-blue-600' : 'text-yellow-600'}`}
				>
					Balance: {formatCurrency(filteredSummary().balance)}
				</span>
			</div>
		</div>
		<div class="flex gap-2">
			{#if filteredTransactions().length > 0}
				<button
					onclick={exportFilteredData}
					class="flex items-center gap-2 rounded-lg bg-green-500 px-4 py-2 text-white transition-colors duration-200 hover:bg-green-600"
				>
					<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
						></path>
					</svg>
					Export Filtered
				</button>
			{/if}
		</div>
	</div>

	<!-- Search and Filter Controls -->
	<div class="mb-6 space-y-4">
		<!-- Basic Filters -->
		<div class="flex flex-col gap-4 sm:flex-row">
			<!-- Search -->
			<div class="flex-1">
				<input
					type="text"
					bind:value={searchTerm}
					placeholder="Search transactions..."
					class="w-full rounded-md border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
				/>
			</div>

			<!-- Filter by Type -->
			<select
				bind:value={filterType}
				class="rounded-md border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				<option value="all">All Types</option>
				<option value="income">Income Only</option>
				<option value="expense">Expenses Only</option>
			</select>

			<!-- Sort Options -->
			<select
				bind:value={sortBy}
				class="rounded-md border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				<option value="date">Sort by Date</option>
				<option value="amount">Sort by Amount</option>
				<option value="category">Sort by Category</option>
				<option value="description">Sort by Description</option>
			</select>

			<button
				onclick={() => (sortOrder = sortOrder === 'asc' ? 'desc' : 'asc')}
				class="rounded-md bg-gray-100 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
				title={sortOrder === 'asc' ? 'Sort Ascending' : 'Sort Descending'}
			>
				{sortOrder === 'asc' ? '↑' : '↓'}
			</button>

			<button
				onclick={toggleAdvancedFilters}
				class="rounded-md bg-blue-100 px-4 py-2 text-blue-700 transition-colors hover:bg-blue-200"
			>
				{showAdvancedFilters ? 'Hide' : 'Advanced'}
			</button>
		</div>

		<!-- Advanced Filters -->
		{#if showAdvancedFilters}
			<div class="space-y-4 rounded-lg bg-gray-50 p-4">
				<h4 class="font-medium text-gray-800">Advanced Filters</h4>

				<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
					<!-- Category Filter -->
					<div>
						<label for="category-filter" class="mb-1 block text-sm font-medium text-gray-700"
							>Category</label
						>
						<select
							id="category-filter"
							bind:value={categoryFilter}
							class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
						>
							<option value="all">All Categories</option>
							{#each availableCategories() as category}
								<option value={category}>{category}</option>
							{/each}
						</select>
					</div>

					<!-- Amount Range -->
					<div>
						<span class="mb-1 block text-sm font-medium text-gray-700">Amount Range</span>
						<div class="flex gap-2">
							<input
								type="number"
								bind:value={amountMin}
								placeholder="Min"
								step="0.01"
								aria-label="Minimum amount"
								class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
							/>
							<input
								type="number"
								bind:value={amountMax}
								placeholder="Max"
								step="0.01"
								aria-label="Maximum amount"
								class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
							/>
						</div>
					</div>

					<!-- Date Range -->
					<div>
						<span class="mb-1 block text-sm font-medium text-gray-700">Date Range</span>
						<div class="flex gap-2">
							<input
								type="date"
								bind:value={dateFrom}
								aria-label="From date"
								class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
							/>
							<input
								type="date"
								bind:value={dateTo}
								aria-label="To date"
								class="w-full rounded-md border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
							/>
						</div>
					</div>
				</div>

				<div class="flex justify-end">
					<button
						onclick={clearAllFilters}
						class="rounded-md bg-gray-500 px-4 py-2 text-white transition-colors hover:bg-gray-600"
					>
						Clear All Filters
					</button>
				</div>
			</div>
		{/if}

		{#if transactions.length > 0}
			<div class="flex items-center justify-between text-sm text-gray-600">
				<span>Showing {filteredTransactions().length} of {transactions.length} transactions</span>
				<button onclick={clearAllTransactions} class="font-medium text-red-600 hover:text-red-800">
					Clear All Transactions
				</button>
			</div>
		{/if}
	</div>

	<!-- Transactions Table/List -->
	{#if filteredTransactions().length === 0}
		<div class="py-12 text-center">
			{#if transactions.length === 0}
				<svg
					class="mx-auto mb-4 h-16 w-16 text-gray-300"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					></path>
				</svg>
				<h3 class="mb-2 text-lg font-medium text-gray-700">No transactions yet</h3>
				<p class="text-gray-500">Add your first transaction to get started!</p>
			{:else}
				<svg
					class="mx-auto mb-4 h-16 w-16 text-gray-300"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
					></path>
				</svg>
				<h3 class="mb-2 text-lg font-medium text-gray-700">No matching transactions</h3>
				<p class="text-gray-500">Try adjusting your search or filter criteria</p>
				<button
					onclick={clearAllFilters}
					class="mt-4 rounded-md bg-blue-500 px-4 py-2 text-white transition-colors hover:bg-blue-600"
				>
					Clear Filters
				</button>
			{/if}
		</div>
	{:else}
		<!-- Desktop Table View -->
		<div class="hidden overflow-x-auto md:block">
			<table class="w-full">
				<thead class="bg-gray-50">
					<tr>
						<th
							class="cursor-pointer px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase hover:bg-gray-100"
							onclick={() => {
								sortBy = 'date';
								sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
							}}
						>
							Date {sortBy === 'date' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
						</th>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Type</th
						>
						<th
							class="cursor-pointer px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase hover:bg-gray-100"
							onclick={() => {
								sortBy = 'amount';
								sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
							}}
						>
							Amount {sortBy === 'amount' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
						</th>
						<th
							class="cursor-pointer px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase hover:bg-gray-100"
							onclick={() => {
								sortBy = 'category';
								sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
							}}
						>
							Category {sortBy === 'category' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
						</th>
						<th
							class="cursor-pointer px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase hover:bg-gray-100"
							onclick={() => {
								sortBy = 'description';
								sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
							}}
						>
							Description {sortBy === 'description' ? (sortOrder === 'asc' ? '↑' : '↓') : ''}
						</th>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Actions</th
						>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each filteredTransactions() as transaction, index}
						<tr class={`hover:bg-gray-50 ${index % 2 === 0 ? 'bg-white' : 'bg-gray-25'}`}>
							<td class="px-4 py-4 text-sm whitespace-nowrap text-gray-700">
								{formatDate(transaction.date)}
							</td>
							<td class="px-4 py-4 whitespace-nowrap">
								<span
									class={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
										transaction.type === 'income'
											? 'bg-green-100 text-green-800'
											: 'bg-red-100 text-red-800'
									}`}
								>
									{transaction.type}
								</span>
							</td>
							<td class="px-4 py-4 text-sm font-medium whitespace-nowrap">
								<span class={transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}>
									{transaction.type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
								</span>
							</td>
							<td class="px-4 py-4 text-sm whitespace-nowrap text-gray-700 capitalize">
								{transaction.category}
							</td>
							<td
								class="max-w-xs truncate px-4 py-4 text-sm text-gray-700"
								title={transaction.description}
							>
								{transaction.description}
							</td>
							<td class="px-4 py-4 text-sm whitespace-nowrap">
								<button
									onclick={() => deleteTransaction(transaction.id)}
									class="rounded p-1 text-red-600 transition-colors hover:bg-red-50 hover:text-red-800"
									aria-label="Delete transaction"
								>
									<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
										></path>
									</svg>
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Mobile Card View -->
		<div class="space-y-4 md:hidden">
			{#each filteredTransactions() as transaction}
				<div class="rounded-lg border border-gray-200 p-4 transition-shadow hover:shadow-md">
					<div class="mb-2 flex items-start justify-between">
						<div>
							<span
								class={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
									transaction.type === 'income'
										? 'bg-green-100 text-green-800'
										: 'bg-red-100 text-red-800'
								}`}
							>
								{transaction.type}
							</span>
							<p class="mt-1 text-sm text-gray-600">{formatDate(transaction.date)}</p>
						</div>
						<div class="flex items-center gap-2">
							<span
								class={`text-lg font-bold ${transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}`}
							>
								{transaction.type === 'income' ? '+' : '-'}{formatCurrency(transaction.amount)}
							</span>
							<button
								onclick={() => deleteTransaction(transaction.id)}
								class="rounded p-1 text-red-600 transition-colors hover:bg-red-50 hover:text-red-800"
								aria-label="Delete transaction"
							>
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
									></path>
								</svg>
							</button>
						</div>
					</div>
					<p class="text-sm font-medium text-gray-700 capitalize">{transaction.category}</p>
					<p class="text-sm text-gray-600">{transaction.description}</p>
				</div>
			{/each}
		</div>
	{/if}
</div>
