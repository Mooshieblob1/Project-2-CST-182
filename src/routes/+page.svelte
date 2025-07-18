<script lang="ts">
	import { onMount } from 'svelte';
	import TransactionForm from '$lib/components/TransactionForm.svelte';
	import TransactionList from '$lib/components/TransactionList.svelte';
	import EnhancedTransactionList from '$lib/components/EnhancedTransactionList.svelte';
	import Summary from '$lib/components/Summary.svelte';
	import EnhancedSummary from '$lib/components/EnhancedSummary.svelte';
	import { transactionStore } from '$lib/stores/transactions';
	import { loadTransactionsFromCSV, parseCSV } from '$lib/csvLoader';
	import type { Transaction } from '$lib/stores/transactions';

	let activeTab = $state('add');
	let transactions = $derived($transactionStore);

	// Save to localStorage whenever transactions change
	$effect(() => {
		if (transactions.length > 0 && typeof localStorage !== 'undefined') {
			localStorage.setItem('finance-transactions', JSON.stringify(transactions));
		}
	});

	onMount(async () => {
		// First, try to load from localStorage
		const saved = localStorage.getItem('finance-transactions');
		let hasLocalData = false;

		if (saved) {
			try {
				const parsed = JSON.parse(saved);
				if (parsed && parsed.length > 0) {
					transactionStore.loadTransactions(parsed);
					hasLocalData = true;
					console.log(`Loaded ${parsed.length} transactions from localStorage`);
				}
			} catch (e) {
				console.error('Failed to load transactions from localStorage:', e);
			}
		}

		// If no localStorage data, automatically load from CSV file
		if (!hasLocalData) {
			try {
				const csvTransactions = await loadTransactionsFromCSV();
				if (csvTransactions.length > 0) {
					console.log(`Auto-loaded ${csvTransactions.length} transactions from CSV file`);
					transactionStore.loadTransactions(csvTransactions);
				}
			} catch (e) {
				console.error('Failed to auto-load transactions from CSV:', e);
			}
		}
	});

	function setActiveTab(tab: string) {
		activeTab = tab;
	}

	function downloadTransactions() {
		if (transactions.length === 0) {
			alert('No transactions to download');
			return;
		}

		// Create CSV content
		const headers = ['Date', 'Type', 'Amount', 'Category', 'Description'];
		const csvContent = [
			headers.join(','),
			...transactions.map((t) =>
				[t.date, t.type, t.amount, t.category, `"${t.description}"`].join(',')
			)
		].join('\n');

		// Create and download file
		const blob = new Blob([csvContent], { type: 'text/csv' });
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `transactions_${new Date().toISOString().split('T')[0]}.csv`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		window.URL.revokeObjectURL(url);
	}

	async function loadCSVData() {
		try {
			const csvTransactions = await loadTransactionsFromCSV();
			if (csvTransactions.length > 0) {
				// Ask user if they want to replace or merge
				const replace = confirm(
					`Found ${csvTransactions.length} transactions in CSV file. Replace current data? (Cancel to merge)`
				);

				if (replace) {
					transactionStore.clearAll();
					// Use setTimeout to ensure the clear operation completes
					setTimeout(() => {
						transactionStore.loadTransactions(csvTransactions);
					}, 10);
				} else {
					// Merge - add new transactions that don't conflict
					csvTransactions.forEach((csvTransaction) => {
						transactionStore.addTransaction(csvTransaction);
					});
				}
				alert(`Successfully loaded ${csvTransactions.length} transactions from CSV`);
			} else {
				alert('No transactions found in CSV file or file not accessible');
			}
		} catch (e) {
			console.error('Failed to load CSV:', e);
			alert('Error loading CSV file: ' + (e as Error).message);
		}
	}

	function handleFileImport(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const csvText = e.target?.result as string;
				const csvTransactions = parseCSV(csvText);

				if (csvTransactions.length > 0) {
					const replace = confirm(
						`Found ${csvTransactions.length} transactions in uploaded file. Replace current data? (Cancel to merge)`
					);

					if (replace) {
						transactionStore.clearAll();
						// Use setTimeout to ensure the clear operation completes
						setTimeout(() => {
							transactionStore.loadTransactions(csvTransactions);
						}, 10);
					} else {
						csvTransactions.forEach((csvTransaction) => {
							transactionStore.addTransaction(csvTransaction);
						});
					}
					alert(`Successfully imported ${csvTransactions.length} transactions`);
				} else {
					alert('No valid transactions found in the uploaded file');
				}
			} catch (error) {
				console.error('Error parsing uploaded CSV:', error);
				alert('Error parsing CSV file: ' + (error as Error).message);
			}
		};
		reader.readAsText(file);

		// Reset input
		input.value = '';
	}

	function resetAndReloadFromCSV() {
		if (confirm('This will clear all current data and reload from CSV. Continue?')) {
			// Clear localStorage
			localStorage.removeItem('finance-transactions');

			// Clear store
			transactionStore.clearAll();

			// Reload from CSV
			setTimeout(async () => {
				try {
					const csvTransactions = await loadTransactionsFromCSV();
					if (csvTransactions.length > 0) {
						transactionStore.loadTransactions(csvTransactions);
						localStorage.setItem('finance-transactions', JSON.stringify(csvTransactions));
						alert(`Reset complete! Loaded ${csvTransactions.length} transactions from CSV`);
					} else {
						alert('No transactions found in CSV file');
					}
				} catch (e) {
					console.error('Failed to reload from CSV:', e);
					alert('Error reloading from CSV: ' + (e as Error).message);
				}
			}, 100);
		}
	}
</script>

<svelte:head>
	<title>Personal Finance Tracker</title>
	<meta
		name="description"
		content="Track your income and expenses with this simple finance tracker"
	/>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
	<div class="container mx-auto px-4 py-8">
		<!-- Header -->
		<div class="mb-8 text-center">
			<h1 class="mb-2 text-4xl font-bold text-gray-800">Personal Finance Tracker</h1>
			<p class="text-gray-600">Manage your income and expenses with ease</p>
		</div>

		<!-- Navigation Tabs -->
		<div class="mb-8 flex justify-center">
			<div class="rounded-lg bg-white p-1 shadow-md">
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'add'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('add')}
				>
					Add Transaction
				</button>
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'summary'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('summary')}
				>
					Summary
				</button>
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'analytics'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('analytics')}
				>
					Analytics
				</button>
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'transactions'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('transactions')}
				>
					Transactions
				</button>
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'manage'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('manage')}
				>
					Manage
				</button>
				<button
					class={`rounded-md px-6 py-3 font-medium transition-all duration-200 ${
						activeTab === 'data'
							? 'bg-blue-500 text-white shadow-md'
							: 'text-gray-600 hover:text-blue-500'
					}`}
					onclick={() => setActiveTab('data')}
				>
					Data
				</button>
			</div>
		</div>

		<!-- Content -->
		<div class="mx-auto max-w-6xl">
			{#if activeTab === 'add'}
				<TransactionForm />
			{:else if activeTab === 'summary'}
				<Summary {transactions} />
			{:else if activeTab === 'analytics'}
				<EnhancedSummary {transactions} />
			{:else if activeTab === 'transactions'}
				<TransactionList {transactions} />
			{:else if activeTab === 'manage'}
				<EnhancedTransactionList {transactions} />
			{:else if activeTab === 'data'}
				<!-- Data Import/Export Section -->
				<div class="space-y-6">
					<!-- CSV Operations -->
					<div class="rounded-lg bg-white p-6 shadow-lg">
						<h2 class="mb-6 text-2xl font-bold text-gray-800">Data Management</h2>

						<!-- Import Section -->
						<div class="mb-8">
							<h3 class="mb-4 text-lg font-semibold text-gray-700">Import Data</h3>
							<div class="grid grid-cols-1 gap-4 md:grid-cols-3">
								<div class="rounded-lg border-2 border-dashed border-gray-300 p-6 text-center">
									<svg
										class="mx-auto mb-4 h-12 w-12 text-gray-400"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
										></path>
									</svg>
									<h4 class="mb-2 text-lg font-medium text-gray-700">Upload CSV File</h4>
									<p class="mb-4 text-gray-500">Import transactions from a CSV file</p>
									<input
										type="file"
										accept=".csv"
										onchange={handleFileImport}
										class="hidden"
										id="csv-upload"
									/>
									<label
										for="csv-upload"
										class="inline-block cursor-pointer rounded-lg bg-blue-500 px-4 py-2 text-white transition-colors hover:bg-blue-600"
									>
										Choose File
									</label>
								</div>

								<div class="rounded-lg border-2 border-dashed border-green-300 p-6 text-center">
									<svg
										class="mx-auto mb-4 h-12 w-12 text-green-400"
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
									<h4 class="mb-2 text-lg font-medium text-gray-700">Load Default CSV</h4>
									<p class="mb-4 text-gray-500">Load transactions from default CSV file</p>
									<button
										onclick={loadCSVData}
										class="rounded-lg bg-green-500 px-4 py-2 text-white transition-colors hover:bg-green-600"
									>
										Load CSV Data
									</button>
								</div>

								<div class="rounded-lg border-2 border-dashed border-orange-300 p-6 text-center">
									<svg
										class="mx-auto mb-4 h-12 w-12 text-orange-400"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
										></path>
									</svg>
									<h4 class="mb-2 text-lg font-medium text-gray-700">Reset & Reload</h4>
									<p class="mb-4 text-gray-500">Clear all data and reload from CSV</p>
									<button
										onclick={resetAndReloadFromCSV}
										class="rounded-lg bg-orange-500 px-4 py-2 text-white transition-colors hover:bg-orange-600"
									>
										Reset & Reload
									</button>
								</div>
							</div>
						</div>

						<!-- Export Section -->
						<div class="mb-8">
							<h3 class="mb-4 text-lg font-semibold text-gray-700">Export Data</h3>
							<div class="rounded-lg bg-gray-50 p-6">
								<div class="flex items-center justify-between">
									<div>
										<h4 class="font-medium text-gray-700">Export to CSV</h4>
										<p class="text-sm text-gray-500">
											Download all your transactions as a CSV file
										</p>
									</div>
									<button
										onclick={downloadTransactions}
										disabled={transactions.length === 0}
										class="flex items-center gap-2 rounded-lg bg-purple-500 px-4 py-2 text-white transition-colors hover:bg-purple-600 disabled:cursor-not-allowed disabled:bg-gray-300"
									>
										<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
											></path>
										</svg>
										Export CSV
									</button>
								</div>
							</div>
						</div>

						<!-- Data Summary -->
						<div class="mb-8">
							<h3 class="mb-4 text-lg font-semibold text-gray-700">Current Data</h3>
							<div class="grid grid-cols-2 gap-4 md:grid-cols-4">
								<div class="rounded-lg bg-blue-50 p-4 text-center">
									<p class="text-2xl font-bold text-blue-600">{transactions.length}</p>
									<p class="text-sm text-blue-600">Total Transactions</p>
								</div>
								<div class="rounded-lg bg-green-50 p-4 text-center">
									<p class="text-2xl font-bold text-green-600">
										{transactions.filter((t) => t.type === 'income').length}
									</p>
									<p class="text-sm text-green-600">Income Entries</p>
								</div>
								<div class="rounded-lg bg-red-50 p-4 text-center">
									<p class="text-2xl font-bold text-red-600">
										{transactions.filter((t) => t.type === 'expense').length}
									</p>
									<p class="text-sm text-red-600">Expense Entries</p>
								</div>
								<div class="rounded-lg bg-gray-50 p-4 text-center">
									<p class="text-2xl font-bold text-gray-600">
										{new Set(transactions.map((t) => t.category)).size}
									</p>
									<p class="text-sm text-gray-600">Categories</p>
								</div>
							</div>
						</div>

						<!-- CSV Format Help -->
						<div class="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
							<h4 class="mb-2 font-medium text-yellow-800">CSV Format</h4>
							<p class="mb-2 text-sm text-yellow-700">
								Your CSV file should have the following format:
							</p>
							<code class="block rounded bg-yellow-100 p-2 text-xs text-yellow-800">
								type,amount,category,description,date<br />
								income,100.0,gift,Gift from Brother,2025-06-06<br />
								expense,200.0,food,Food,2025-06-06
							</code>
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Footer -->
		<div class="mt-12 text-center text-gray-500">
			<p>Total Transactions: {transactions.length}</p>
		</div>
	</div>
</div>
