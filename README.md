# Personal Finance Tracker

A simple command-line personal finance tracker written in Python that helps you manage your income and expenses, view financial summaries, and persist data to CSV files.

## Features

- **Add Transactions**: Record income and expense transactions with details like amount, category, description, and date
- **View Financial Summary**: See total income, expenses, balance, and expenses broken down by category
- **View All Transactions**: Display a formatted table of all recorded transactions
- **Data Persistence**: Automatically save and load transactions from a CSV file
- **Input Validation**: Ensures valid data entry for amounts, dates, and transaction types

## Getting Started

### Prerequisites

- Python 3.x
- No external dependencies required (uses only built-in Python libraries)

### Installation

1. Clone or download the project files
2. Ensure you have `finance_tracker.py` in your project directory
3. Run the program:

```bash
python finance_tracker.py
```

## Usage

When you run the program, you'll see a menu with the following options:

### 1. Add Transaction
- Choose between "income" or "expense"
- Enter the amount (must be greater than 0)
- Specify a category (e.g., food, rent, salary)
- Add a description
- Enter a date in YYYY-MM-DD format (or leave blank for today's date)

### 2. View Summary
Displays:
- Total income
- Total expenses
- Current balance (income - expenses)
- Breakdown of expenses by category

### 3. Save & Exit
- Saves all transactions to `transactions.csv`
- Shows final summary
- Exits the program

### 4. View All Transactions
Shows a formatted table with all transactions including:
- Date
- Type (Income/Expense)
- Amount
- Category
- Description

## Data Storage

The program uses a CSV file (`transactions.csv`) to store transaction data with the following structure:

```csv
type,amount,category,description,date
income,2100.0,salary,Salary,2025-06-06
expense,200.0,food,Groceries,2025-06-06
```

### Automatic Loading
- When the program starts, it automatically loads existing transactions from `transactions.csv`
- If no file exists, it starts with an empty transaction list

### Automatic Saving
- Data is saved when you choose option 3 (Save & Exit)
- All transactions are written to the CSV file for future sessions

## Input Validation

The program includes validation for:
- **Transaction Type**: Must be "income" or "expense"
- **Amount**: Must be a positive number
- **Date Format**: Must be in YYYY-MM-DD format
- **Numeric Input**: Handles invalid number entries gracefully

## Example Session

```
--- Personal Finance Tracker ---
1. Add Transaction
2. View Summary
3. Save & Exit
4. View All Transactions
Choose an option (1–4): 1

Type (income/expense): income
Amount: $2500
Category (e.g. food, rent, salary): salary
Description: Monthly salary
Date (YYYY-MM-DD) [Leave blank for today]: 2025-07-18
Transaction added.

--- Personal Finance Tracker ---
1. Add Transaction
2. View Summary
3. Save & Exit
4. View All Transactions
Choose an option (1–4): 2

--- Financial Summary ---
Total Income: $2500.00
Total Expenses: $0.00
Balance: $2500.00

--- Expenses by Category ---
No expense data available.
```

## File Structure

```
Project/
├── finance_tracker.py    # Main application file
├── transactions.csv      # Data storage (created automatically)
└── README.md            # This documentation
```

## Code Structure

### Main Functions

- `load_from_file()`: Loads existing transactions from CSV
- `add_transaction()`: Handles adding new transactions with validation
- `view_summary()`: Calculates and displays financial summary
- `view_all_transactions()`: Shows formatted table of all transactions
- `save_to_file()`: Saves transactions to CSV file
- `display_menu()`: Shows the main menu options
- `main()`: Main program loop

### Data Structure

Transactions are stored as dictionaries with the following keys:
- `type`: "income" or "expense"
- `amount`: Float value
- `category`: String category name
- `description`: String description
- `date`: Date in YYYY-MM-DD format

## Contributing

Feel free to fork this project and submit pull requests for improvements such as:
- Additional validation features
- Export to different file formats
- Graphical data visualization
- Budget tracking and alerts
- Multiple account support

## License

This project is open source and available under the MIT License.
