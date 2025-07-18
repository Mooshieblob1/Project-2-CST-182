import type { Transaction } from './stores/transactions';

export async function loadTransactionsFromCSV(): Promise<Transaction[]> {
	try {
		// Try to fetch the CSV file from the public directory
		const response = await fetch('/transactions.csv');
		if (!response.ok) {
			console.log('No transactions.csv file found in public directory');
			return [];
		}

		const csvText = await response.text();
		return parseCSV(csvText);
	} catch (error) {
		console.error('Error loading CSV file:', error);
		return [];
	}
}

export function parseCSV(csvText: string): Transaction[] {
	const lines = csvText.split('\n').filter((line) => line.trim());
	if (lines.length <= 1) return []; // No data or just headers

	// Skip header line
	const transactions: Transaction[] = [];

	for (let i = 1; i < lines.length; i++) {
		const values = parseCSVLine(lines[i]);
		if (values.length >= 5) {
			const transaction: Transaction = {
				id: crypto.randomUUID(),
				type: values[0].trim() as 'income' | 'expense',
				amount: parseFloat(values[1]) || 0,
				category: values[2].trim(),
				description: values[3].replace(/^"|"$/g, '').trim(), // Remove quotes
				date: values[4].trim()
			};

			// Validate the transaction
			if (transaction.type && (transaction.type === 'income' || transaction.type === 'expense')) {
				transactions.push(transaction);
			}
		}
	}

	return transactions;
}

function parseCSVLine(line: string): string[] {
	const result: string[] = [];
	let current = '';
	let inQuotes = false;

	for (let i = 0; i < line.length; i++) {
		const char = line[i];

		if (char === '"') {
			inQuotes = !inQuotes;
		} else if (char === ',' && !inQuotes) {
			result.push(current);
			current = '';
		} else {
			current += char;
		}
	}

	result.push(current);
	return result;
}
