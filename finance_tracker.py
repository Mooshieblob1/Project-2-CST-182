"""Personal Finance Tracker - CLI application for managing income and expenses.

This module provides functionality to track financial transactions, categorize 
expenses, view summaries, and persist data to CSV files.
"""
import csv
import os
from datetime import datetime

transactions = []

def load_from_file(filename="transactions.csv"):
    """Load transaction data from CSV file into global transactions list.
    
    Args:
        filename: CSV file path, defaults to "transactions.csv"
    """
    if not os.path.exists(filename):
        return

    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["amount"] = float(row["amount"])
            transactions.append(row)
    print(f"Loaded {len(transactions)} transactions from file.")


def display_menu():
    """Display the main menu options to the user."""
    print("\n--- Personal Finance Tracker ---")
    print("1. Add Transaction")
    print("2. View Summary")
    print("3. Save & Exit")
    print("4. View All Transactions")

def add_transaction():
    """Collect and validate user input to create a new transaction.
    
    Prompts for transaction type, amount, category, description, and date.
    Validates all inputs before adding to transactions list.
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
    """Calculate and display financial overview with category breakdown."""
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
    """Display all transactions in a formatted table."""
    if not transactions:
        print("No transactions to show.")
        return

    print("\n--- All Transactions ---")
    print(f"{'Date':<12} {'Type':<8} {'Amount':>10}  {'Category':<15} {'Description':<30}")
    print("-" * 78)

    for t in transactions:
        print(f"{t['date']:<12} {t['type'].capitalize():<8} ${t['amount']:>9.2f}  {t['category']:<15} {t['description']:<30}")


def save_to_file(filename="transactions.csv"):
    """Save all transactions to CSV file.
    
    Args:
        filename: Output file path. Defaults to "transactions.csv".
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["type", "amount", "category", "description", "date"])
        writer.writeheader()
        for t in transactions:
            writer.writerow(t)
    print("Data saved to file.")

def main():
    """Run the main application loop.
    
    Loads existing transactions and presents an interactive menu allowing users
    to add transactions, view summaries, view all transactions, or save and exit.
    """
    load_from_file()
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