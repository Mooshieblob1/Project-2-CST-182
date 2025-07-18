<script lang="ts">
	import { onMount } from 'svelte';
	import TransactionForm from '$lib/components/TransactionForm.svelte';
	import TransactionList from '$lib/components/TransactionList.svelte';
	import EnhancedTransactionList from '$lib/components/EnhancedTransactionList.svelte';
	import Summary from '$lib/components/Summary.svelte';
	import EnhancedSummary from '$lib/components/EnhancedSummary.svelte';
	import { transactionStore } from '$lib/stores/transactions';
	import type { Transaction } from '$lib/stores/transactions';

	let activeTab = $state('add');
	let transactions = $state<Transaction[]>([]);

	onMount(() => {
		// Load transactions from localStorage on component mount
		const saved = localStorage.getItem('finance-transactions');
		if (saved) {
			try {
				const parsed = JSON.parse(saved);
				transactionStore.loadTransactions(parsed);
				transactions = parsed;
			} catch (e) {
				console.error('Failed to load transactions from localStorage:', e);
			}
		}

		// Subscribe to transaction store changes
		return transactionStore.subscribe((value: Transaction[]) => {
			transactions = value;
			// Save to localStorage whenever transactions change
			localStorage.setItem('finance-transactions', JSON.stringify(value));
		});
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
			{/if}
		</div>

		<!-- Footer -->
		<div class="mt-12 text-center text-gray-500">
			<p>Total Transactions: {transactions.length}</p>
		</div>
	</div>
</div>
