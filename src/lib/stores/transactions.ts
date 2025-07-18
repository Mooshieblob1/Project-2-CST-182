import { writable } from 'svelte/store';

export interface Transaction {
	id: string;
	type: 'income' | 'expense';
	amount: number;
	category: string;
	description: string;
	date: string;
}

function createTransactionStore() {
	const { subscribe, set, update } = writable<Transaction[]>([]);

	return {
		subscribe,
		addTransaction: (transaction: Omit<Transaction, 'id'>) => {
			const newTransaction: Transaction = {
				...transaction,
				id: crypto.randomUUID()
			};
			update((transactions) => [...transactions, newTransaction]);
		},
		removeTransaction: (id: string) => {
			update((transactions) => transactions.filter((t) => t.id !== id));
		},
		clearAll: () => {
			set([]);
		},
		loadTransactions: (transactions: Transaction[]) => {
			set(transactions);
		}
	};
}

export const transactionStore = createTransactionStore();
