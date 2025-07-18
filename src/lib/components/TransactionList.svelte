<script lang="ts">
	import { transactionStore } from '../stores/transactions';

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
	let selectedCategory = $state('all');
	let dateFrom = $state('');
	let dateTo = $state('');
	let amountMin = $state('');
	let amountMax = $state('');

	// Get unique categories for filter
	let categories = $derived(() => {
		const uniqueCategories = [...new Set(transactions.map((t) => t.category))];
		return uniqueCategories.sort();
	});

	// Enhanced filtered and sorted transactions
	let filteredTransactions = $derived(() => {
		let filtered = transactions;

		// Filter by type
		if (filterType !== 'all') {
			filtered = filtered.filter((t) => t.type === filterType);
		}

		// Filter by category
		if (selectedCategory !== 'all') {
			filtered = filtered.filter((t) => t.category === selectedCategory);
		}

		// Search filter
		if (searchTerm.trim()) {
			const search = searchTerm.toLowerCase();
			filtered = filtered.filter(
				(t) =>
					t.description.toLowerCase().includes(search) ||
					t.category.toLowerCase().includes(search) ||
					t.type.toLowerCase().includes(search)
			);
		}

		// Date range filter
		if (dateFrom) {
			filtered = filtered.filter((t) => new Date(t.date) >= new Date(dateFrom));
		}
		if (dateTo) {
			filtered = filtered.filter((t) => new Date(t.date) <= new Date(dateTo));
		}

		// Amount range filter
		if (amountMin) {
			filtered = filtered.filter((t) => t.amount >= parseFloat(amountMin));
		}
		if (amountMax) {
			filtered = filtered.filter((t) => t.amount <= parseFloat(amountMax));
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

	// Calculate totals for filtered transactions
	let filteredTotals = $derived(() => {
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

	function clearFilters() {
		filterType = 'all';
		selectedCategory = 'all';
		searchTerm = '';
		dateFrom = '';
		dateTo = '';
		amountMin = '';
		amountMax = '';
	}

	function exportFiltered() {
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
</script>

<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
	<!-- Search and Filter Controls -->
	<div class="mb-6 space-y-4">
		<!-- Primary Filters -->
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

			<!-- Filter by Category -->
			<select
				bind:value={selectedCategory}
				class="rounded-md border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				<option value="all">All Categories</option>
				{#each categories() as category}
					<option value={category}>{category}</option>
				{/each}
			</select>

			<!-- Sort Options -->
			<select
				bind:value={sortBy}
				class="rounded-md border border-gray-300 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
			>
				<option value="date">Sort by Date</option>
				<option value="amount">Sort by Amount</option>
				<option value="category">Sort by Category</option>
			</select>

			<button
				onclick={() => (sortOrder = sortOrder === 'asc' ? 'desc' : 'asc')}
				class="rounded-md bg-gray-100 px-4 py-2 text-gray-700 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
			>
				{sortOrder === 'asc' ? '↑' : '↓'}
			</button>
		</div>

		<!-- Advanced Filters -->
		<details class="group">
			<summary class="mb-3 cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-800">
				Advanced Filters {filteredTransactions().length !== transactions.length ? '(Active)' : ''}
			</summary>
			<div class="grid grid-cols-1 gap-4 rounded-md bg-gray-50 p-4 md:grid-cols-2 lg:grid-cols-4">
				<!-- Date Range -->
				<div>
					<label for="dateFrom" class="mb-1 block text-xs font-medium text-gray-600"
						>From Date</label
					>
					<input
						id="dateFrom"
						type="date"
						bind:value={dateFrom}
						class="w-full rounded border border-gray-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>
				<div>
					<label for="dateTo" class="mb-1 block text-xs font-medium text-gray-600">To Date</label>
					<input
						id="dateTo"
						type="date"
						bind:value={dateTo}
						class="w-full rounded border border-gray-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>

				<!-- Amount Range -->
				<div>
					<label for="amountMin" class="mb-1 block text-xs font-medium text-gray-600"
						>Min Amount</label
					>
					<input
						id="amountMin"
						type="number"
						bind:value={amountMin}
						step="0.01"
						placeholder="0.00"
						class="w-full rounded border border-gray-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>
				<div>
					<label for="amountMax" class="mb-1 block text-xs font-medium text-gray-600"
						>Max Amount</label
					>
					<input
						id="amountMax"
						type="number"
						bind:value={amountMax}
						step="0.01"
						placeholder="0.00"
						class="w-full rounded border border-gray-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
					/>
				</div>
			</div>
		</details>

		<!-- Summary and Actions -->
		{#if transactions.length > 0}
			<div
				class="flex flex-col items-start justify-between gap-4 text-sm sm:flex-row sm:items-center"
			>
				<div class="text-gray-600">
					<p class="font-medium">
						Showing {filteredTransactions().length} of {transactions.length} transactions
					</p>
					{#if filteredTransactions().length !== transactions.length}
						<div class="mt-1 space-y-1 text-xs">
							<p>
								Income: <span class="font-medium text-green-600"
									>{formatCurrency(filteredTotals().income)}</span
								>
							</p>
							<p>
								Expenses: <span class="font-medium text-red-600"
									>{formatCurrency(filteredTotals().expenses)}</span
								>
							</p>
							<p>
								Balance: <span
									class="font-medium {filteredTotals().balance >= 0
										? 'text-blue-600'
										: 'text-yellow-600'}">{formatCurrency(filteredTotals().balance)}</span
								>
							</p>
						</div>
					{/if}
				</div>
				<div class="flex gap-2">
					{#if filteredTransactions().length !== transactions.length}
						<button
							onclick={clearFilters}
							class="text-sm font-medium text-blue-600 hover:text-blue-800"
						>
							Clear Filters
						</button>
						<button
							onclick={exportFiltered}
							class="rounded bg-green-500 px-3 py-1 text-sm text-white transition-colors hover:bg-green-600"
						>
							Export Filtered
						</button>
					{/if}
					<button
						onclick={clearAllTransactions}
						class="text-sm font-medium text-red-600 hover:text-red-800"
					>
						Clear All
					</button>
				</div>
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
			{/if}
		</div>
	{:else}
		<!-- Desktop Table View -->
		<div class="hidden overflow-x-auto md:block">
			<table class="w-full">
				<thead class="bg-gray-50">
					<tr>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Date</th
						>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Type</th
						>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Amount</th
						>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Category</th
						>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Description</th
						>
						<th
							class="px-4 py-3 text-left text-xs font-medium tracking-wider text-gray-500 uppercase"
							>Actions</th
						>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each filteredTransactions() as transaction}
						<tr class="hover:bg-gray-50">
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
							<td class="px-4 py-4 text-sm text-gray-700">
								{transaction.description}
							</td>
							<td class="px-4 py-4 text-sm whitespace-nowrap">
								<button
									onclick={() => deleteTransaction(transaction.id)}
									class="text-red-600 transition-colors hover:text-red-800"
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
				<div class="rounded-lg border border-gray-200 p-4">
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
								class="p-1 text-red-600 transition-colors hover:text-red-800"
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
