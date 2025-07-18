<script lang="ts">
	import { transactionStore } from '$lib';

	let formData = $state({
		type: 'expense' as 'income' | 'expense',
		amount: '',
		category: '',
		description: '',
		date: new Date().toISOString().split('T')[0]
	});

	let errors = $state({
		amount: '',
		category: '',
		description: '',
		date: ''
	});

	function validateForm() {
		errors = { amount: '', category: '', description: '', date: '' };
		let isValid = true;

		// Validate amount
		const amount = parseFloat(formData.amount);
		if (!formData.amount || isNaN(amount) || amount <= 0) {
			errors.amount = 'Amount must be a positive number';
			isValid = false;
		}

		// Validate category
		if (!formData.category.trim()) {
			errors.category = 'Category is required';
			isValid = false;
		}

		// Validate description
		if (!formData.description.trim()) {
			errors.description = 'Description is required';
			isValid = false;
		}

		// Validate date
		if (!formData.date) {
			errors.date = 'Date is required';
			isValid = false;
		}

		return isValid;
	}

	function handleSubmit(event: Event) {
		event.preventDefault();

		if (!validateForm()) {
			return;
		}

		transactionStore.addTransaction({
			type: formData.type,
			amount: parseFloat(formData.amount),
			category: formData.category.trim(),
			description: formData.description.trim(),
			date: formData.date
		});

		// Reset form
		formData = {
			type: 'expense',
			amount: '',
			category: '',
			description: '',
			date: new Date().toISOString().split('T')[0]
		};

		// Show success message
		showSuccessMessage();
	}

	let showSuccess = $state(false);
	function showSuccessMessage() {
		showSuccess = true;
		setTimeout(() => {
			showSuccess = false;
		}, 3000);
	}

	// Common categories for quick selection
	const incomeCategories = ['Salary', 'Freelance', 'Investment', 'Gift', 'Other'];
	const expenseCategories = [
		'Food',
		'Rent',
		'Transportation',
		'Entertainment',
		'Healthcare',
		'Shopping',
		'Utilities',
		'Other'
	];
</script>

<div class="mx-auto max-w-2xl rounded-lg bg-white p-6 shadow-lg">
	<h2 class="mb-6 text-2xl font-bold text-gray-800">Add New Transaction</h2>

	{#if showSuccess}
		<div
			class="mb-4 rounded border border-green-400 bg-green-100 px-4 py-3 text-green-700"
			role="alert"
		>
			<span class="block sm:inline">Transaction added successfully!</span>
		</div>
	{/if}

	<form onsubmit={handleSubmit} class="space-y-6">
		<!-- Transaction Type -->
		<fieldset>
			<legend class="mb-2 block text-sm font-medium text-gray-700">Transaction Type</legend>
			<div class="flex space-x-4">
				<label class="flex items-center">
					<input
						type="radio"
						bind:group={formData.type}
						value="income"
						class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-blue-500"
					/>
					<span class="ml-2 text-sm font-medium text-gray-700">Income</span>
				</label>
				<label class="flex items-center">
					<input
						type="radio"
						bind:group={formData.type}
						value="expense"
						class="h-4 w-4 border-gray-300 bg-gray-100 text-blue-600 focus:ring-blue-500"
					/>
					<span class="ml-2 text-sm font-medium text-gray-700">Expense</span>
				</label>
			</div>
		</fieldset>

		<!-- Amount -->
		<div>
			<label for="amount" class="mb-2 block text-sm font-medium text-gray-700">Amount ($)</label>
			<input
				type="number"
				id="amount"
				bind:value={formData.amount}
				step="0.01"
				min="0"
				class={`w-full rounded-md border px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none ${
					errors.amount ? 'border-red-500' : 'border-gray-300'
				}`}
				placeholder="0.00"
			/>
			{#if errors.amount}
				<p class="mt-1 text-sm text-red-600">{errors.amount}</p>
			{/if}
		</div>

		<!-- Category -->
		<div>
			<label for="category" class="mb-2 block text-sm font-medium text-gray-700">Category</label>
			<div class="space-y-2">
				<input
					type="text"
					id="category"
					bind:value={formData.category}
					class={`w-full rounded-md border px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none ${
						errors.category ? 'border-red-500' : 'border-gray-300'
					}`}
					placeholder="Enter category or select from below"
				/>
				<div class="flex flex-wrap gap-2">
					{#each formData.type === 'income' ? incomeCategories : expenseCategories as category}
						<button
							type="button"
							onclick={() => (formData.category = category)}
							class="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700 transition-colors hover:bg-gray-200"
						>
							{category}
						</button>
					{/each}
				</div>
			</div>
			{#if errors.category}
				<p class="mt-1 text-sm text-red-600">{errors.category}</p>
			{/if}
		</div>

		<!-- Description -->
		<div>
			<label for="description" class="mb-2 block text-sm font-medium text-gray-700"
				>Description</label
			>
			<input
				type="text"
				id="description"
				bind:value={formData.description}
				class={`w-full rounded-md border px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none ${
					errors.description ? 'border-red-500' : 'border-gray-300'
				}`}
				placeholder="Brief description of the transaction"
			/>
			{#if errors.description}
				<p class="mt-1 text-sm text-red-600">{errors.description}</p>
			{/if}
		</div>

		<!-- Date -->
		<div>
			<label for="date" class="mb-2 block text-sm font-medium text-gray-700">Date</label>
			<input
				type="date"
				id="date"
				bind:value={formData.date}
				class={`w-full rounded-md border px-3 py-2 shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none ${
					errors.date ? 'border-red-500' : 'border-gray-300'
				}`}
			/>
			{#if errors.date}
				<p class="mt-1 text-sm text-red-600">{errors.date}</p>
			{/if}
		</div>

		<!-- Submit Button -->
		<button
			type="submit"
			class={`w-full rounded-md px-4 py-3 font-medium text-white transition-colors duration-200 ${
				formData.type === 'income'
					? 'bg-green-500 hover:bg-green-600'
					: 'bg-red-500 hover:bg-red-600'
			}`}
		>
			Add {formData.type === 'income' ? 'Income' : 'Expense'}
		</button>
	</form>
</div>
