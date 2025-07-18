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
	let availableCategories = $derived.by(() => {
		const categories = new Set<string>();
		transactions.forEach((t) => categories.add(t.category));
		return Array.from(categories).sort();
	});

	// Enhanced filtered and sorted transactions
	let filteredTransactions = $derived.by(() => {
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
	let filteredSummary = $derived.by(() => {
		const income = filteredTransactions
			.filter((t) => t.type === 'income')
			.reduce((sum, t) => sum + t.amount, 0);
		const expenses = filteredTransactions
			.filter((t) => t.type === 'expense')
			.reduce((sum, t) => sum + t.amount, 0);
		return {
			income,
			expenses,
			balance: income - expenses,
			count: filteredTransactions.length
		};
	});

	function handleSort(field: string) {
		if (sortBy === field) {
			sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			sortBy = field;
			sortOrder = 'desc';
		}
	}

	function resetFilters() {
		filterType = 'all';
		searchTerm = '';
		categoryFilter = 'all';
		amountMin = '';
		amountMax = '';
		dateFrom = '';
		dateTo = '';
	}

	function deleteTransaction(id: string) {
		if (confirm('Are you sure you want to delete this transaction?')) {
			transactionStore.removeTransaction(id);
		}
	}
</script>

<div class="space-y-6 rounded-lg bg-gray-800 p-6 text-white shadow-lg">
	<h2 class="text-2xl font-bold">Manage Transactions</h2>

	<!-- Filter Controls -->
	<div class="space-y-4">
		<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
			<!-- Search -->
			<input
				type="text"
				placeholder="Search description or category..."
				bind:value={searchTerm}
				class="rounded-lg border-gray-600 bg-gray-700 p-2 focus:border-blue-500 focus:ring-blue-500"
			/>

			<!-- Filter by Type -->
			<select
				bind:value={filterType}
				class="rounded-lg border-gray-600 bg-gray-700 p-2 focus:border-blue-500 focus:ring-blue-500"
			>
				<option value="all">All Types</option>
				<option value="income">Income</option>
				<option value="expense">Expense</option>
			</select>

			<!-- Filter by Category -->
			<select
				bind:value={categoryFilter}
				class="rounded-lg border-gray-600 bg-gray-700 p-2 focus:border-blue-500 focus:ring-blue-500"
			>
				<option value="all">All Categories</option>
				{#each availableCategories as category}
					<option value={category}>{category}</option>
				{/each}
			</select>
		</div>

		<!-- Advanced Filters Toggle -->
		<button
			onclick={() => (showAdvancedFilters = !showAdvancedFilters)}
			class="text-blue-400 hover:underline"
		>
			{showAdvancedFilters ? 'Hide' : 'Show'} Advanced Filters
		</button>

		<!-- Advanced Filters -->
		{#if showAdvancedFilters}
			<div class="grid grid-cols-1 gap-4 rounded-lg bg-gray-700 p-4 md:grid-cols-2">
				<!-- Amount Range -->
				<div class="flex items-center space-x-2">
					<input
						type="number"
						placeholder="Min Amount"
						bind:value={amountMin}
						class="w-full rounded-lg border-gray-500 bg-gray-600 p-2"
					/>
					<span>-</span>
					<input
						type="number"
						placeholder="Max Amount"
						bind:value={amountMax}
						class="w-full rounded-lg border-gray-500 bg-gray-600 p-2"
					/>
				</div>

				<!-- Date Range -->
				<div class="flex items-center space-x-2">
					<input
						type="date"
						bind:value={dateFrom}
						class="w-full rounded-lg border-gray-500 bg-gray-600 p-2"
					/>
					<span>-</span>
					<input
						type="date"
						bind:value={dateTo}
						class="w-full rounded-lg border-gray-500 bg-gray-600 p-2"
					/>
				</div>
			</div>
		{/if}

		<!-- Reset Button -->
		<button onclick={resetFilters} class="rounded-lg bg-gray-600 px-4 py-2 hover:bg-gray-500">
			Reset Filters
		</button>
	</div>

	<!-- Filtered Summary -->
	<div class="grid grid-cols-2 gap-4 rounded-lg bg-gray-700 p-4 md:grid-cols-4">
		<div class="text-center">
			<p class="text-xl font-bold">{filteredSummary.count}</p>
			<p class="text-sm text-gray-400">Transactions</p>
		</div>
		<div class="text-center">
			<p class="text-xl font-bold text-green-400">${filteredSummary.income.toFixed(2)}</p>
			<p class="text-sm text-gray-400">Total Income</p>
		</div>
		<div class="text-center">
			<p class="text-xl font-bold text-red-400">${filteredSummary.expenses.toFixed(2)}</p>
			<p class="text-sm text-gray-400">Total Expenses</p>
		</div>
		<div class="text-center">
			<p class="text-xl font-bold">${filteredSummary.balance.toFixed(2)}</p>
			<p class="text-sm text-gray-400">Balance</p>
		</div>
	</div>

	<!-- Transactions Table -->
	<div class="overflow-x-auto">
		<table class="min-w-full table-auto">
			<thead class="bg-gray-700">
				<tr>
					{#each ['date', 'type', 'amount', 'category', 'description'] as field}
						<th class="px-4 py-2 text-left">
							<button onclick={() => handleSort(field)} class="flex items-center space-x-1">
								<span>{field.charAt(0).toUpperCase() + field.slice(1)}</span>
								{#if sortBy === field}
									<span class="text-lg">
										{sortOrder === 'asc' ? '▲' : '▼'}
									</span>
								{/if}
							</button>
						</th>
					{/each}
					<th class="px-4 py-2 text-left">Actions</th>
				</tr>
			</thead>
			<tbody>
				{#if filteredTransactions.length > 0}
					{#each filteredTransactions as transaction (transaction.id)}
						<tr class="border-b border-gray-700 hover:bg-gray-600">
							<td class="px-4 py-2">{transaction.date}</td>
							<td class="px-4 py-2">
								<span
									class={`rounded-full px-2 py-1 text-xs font-semibold ${
										transaction.type === 'income'
											? 'bg-green-800 text-green-200'
											: 'bg-red-800 text-red-200'
									}`}
								>
									{transaction.type}
								</span>
							</td>
							<td class="px-4 py-2">${transaction.amount.toFixed(2)}</td>
							<td class="px-4 py-2">{transaction.category}</td>
							<td class="px-4 py-2">{transaction.description}</td>
							<td class="px-4 py-2">
								<button
									onclick={() => deleteTransaction(transaction.id)}
									class="text-red-400 hover:text-red-300"
								>
									Delete
								</button>
							</td>
						</tr>
					{/each}
				{:else}
					<tr>
						<td colspan="6" class="py-4 text-center text-gray-400">No transactions found.</td>
					</tr>
				{/if}
			</tbody>
		</table>
	</div>
</div>
