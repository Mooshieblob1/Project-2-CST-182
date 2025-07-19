import csv
import os
from datetime import datetime

transactions = []

def load_from_file(filename="transactions.csv"):
    """
    Load transactions from a CSV file into the global transactions list.
    
    Args:
        filename (str): The name of the CSV file to load from. Defaults to "transactions.csv".
    
    Returns:
        None: The function modifies the global transactions list in place.
    """
    if not os.path.exists(filename):
        return  # No file yet, so nothing to load

    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert amount from string to float
            row["amount"] = float(row["amount"])
            transactions.append(row)
    print(f"Loaded {len(transactions)} transactions from file.")


def display_menu():
    """
    Display the main menu options for the Personal Finance Tracker.
    
    Prints the available menu options to the console:
    1. Add Transaction
    2. View Summary
    3. Save & Exit
    4. View All Transactions
    """
    print("\n--- Personal Finance Tracker ---")
    print("1. Add Transaction")
    print("2. View Summary")
    print("3. Save & Exit")
    print("4. View All Transactions")

def add_transaction():
    """
    Add a new income or expense transaction to the global transactions list.
    
    Prompts the user for transaction details including:
    - Type (income or expense)
    - Amount (must be positive)
    - Category (e.g., food, rent, salary)
    - Description
    - Date (YYYY-MM-DD format, defaults to today if not provided)
    
    Validates all inputs and adds the transaction to the global list if valid.
    Prints error messages for invalid inputs.
    """
    t_type = input("Type (income/expense): ").strip().lower()
    if t_type not in ['income', 'expense']:
        print("Invalid type.")
        return

    try:
        amount = float(input("Amount: $"))
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    category = input("Category (e.g. food, rent, salary): ").strip()
    description = input("Description: ").strip()
    date = input("Date (YYYY-MM-DD) [Leave blank for today]: ").strip()
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')

    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    transactions.append({
        "type": t_type,
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    })
    print("Transaction added.")

def view_summary():
    """
    Display a financial summary of all transactions.
    
    Calculates and displays:
    - Total income
    - Total expenses
    - Current balance (income - expenses)
    - Expenses broken down by category
    
    The summary is printed to the console in a formatted layout.
    """
    income = sum(t["amount"] for t in transactions if t["type"] == "income")
    expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = income - expense

    print("\n--- Financial Summary ---")
    print(f"Total Income: ${income:.2f}")
    print(f"Total Expenses: ${expense:.2f}")
    print(f"Balance: ${balance:.2f}")

    print("\n--- Expenses by Category ---")
    category_totals = {}
    for t in transactions:
        if t["type"] == "expense":
            cat = t["category"]
            category_totals[cat] = category_totals.get(cat, 0) + t["amount"]

    if category_totals:
        for cat, total in category_totals.items():
            print(f"{cat.capitalize():<15} ${total:>8.2f}")
    else:
        print("No expense data available.")

def view_all_transactions():
    """
    Display all transactions in a formatted table.
    
    Shows all transactions with the following columns:
    - Date
    - Type (Income/Expense)
    - Amount
    - Category
    - Description
    
    If no transactions exist, displays a message indicating this.
    """
    if not transactions:
        print("No transactions to show.")
        return

    print("\n--- All Transactions ---")
    # Header
    print(f"{'Date':<12} {'Type':<8} {'Amount':>10}  {'Category':<15} {'Description':<30}")
    print("-" * 78) # Adjusted separator length

    for t in transactions:
        # Data rows
        print(f"{t['date']:<12} {t['type'].capitalize():<8} ${t['amount']:>9.2f}  {t['category']:<15} {t['description']:<30}")


def save_to_file(filename="transactions.csv"):
    """
    Save all transactions to a CSV file.
    
    Args:
        filename (str): The name of the CSV file to save to. Defaults to "transactions.csv".
    
    The CSV file will include the following columns:
    - type: "income" or "expense"
    - amount: Transaction amount as float
    - category: Transaction category
    - description: Transaction description
    - date: Transaction date in YYYY-MM-DD format
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["type", "amount", "category", "description", "date"])
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)
    print("Data saved to file.")

def main():
    """
    Main function that runs the Personal Finance Tracker application.
    
    Loads existing transactions from file, then displays a menu loop allowing users to:
    - Add new transactions
    - View financial summary
    - View all transactions
    - Save data and exit
    
    The loop continues until the user chooses to save and exit (option 3).
    """
    load_from_file() # Load transactions at the start
    while True:
        display_menu()
        choice = input("Choose an option (1–4): ").strip()

        if choice == '1':
            add_transaction()
        elif choice == '2':
            view_summary()
        elif choice == '3':
            save_to_file()
            print(f"\nYou logged {len(transactions)} transactions.")
            view_summary()
            print("Goodbye!")
            break
        elif choice == '4':
            view_all_transactions()
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()