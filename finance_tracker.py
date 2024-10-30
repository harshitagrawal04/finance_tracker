import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime, date
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import Calendar
import os
import ast
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class FinanceTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Finance Tracker")
        self.master.geometry("800x600")
        self.master.configure(bg="#2C3E50")

        self.data_folder = os.path.join(os.path.dirname(__file__), "finance_data")
        
        # Ensure the data folder exists
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.expenses_file = os.path.join(self.data_folder, "expenses.json")
        self.income_file = os.path.join(self.data_folder, "income.json")
        self.categories_file = os.path.join(self.data_folder, "categories.json")

        self.expenses = []
        self.income = []
        self.categories = {
            "income": [],
            "expense": [],
            "spending_limits": {},
            "recurring": {
                "income": [],
                "expense": []
            }
        }

        self.load_data()

        self.create_widgets()

        self.base_dir = os.path.dirname(__file__)  # Base directory for saving files
        
        # Call to update remaining budget on initialization
        self.update_remaining_budget()  # {{ edit_1 }}

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tabs
        tab_control = ttk.Notebook(main_frame)
        
        add_tab = ttk.Frame(tab_control)
        view_tab = ttk.Frame(tab_control)
        analysis_tab = ttk.Frame(tab_control)
        category_tab = ttk.Frame(tab_control)
        
        tab_control.add(add_tab, text="Add Record")
        tab_control.add(view_tab, text="View Records")
        tab_control.add(analysis_tab, text="Analysis")
        tab_control.add(category_tab, text="Manage Categories")
        
        tab_control.pack(expand=1, fill="both")

        # Add Record Tab
        self.create_add_record_widgets(add_tab)

        # View Records Tab
        self.create_view_records_widgets(view_tab)

        # Analysis Tab
        self.create_analysis_widgets(analysis_tab)

        # Category Management Tab
        self.create_category_management_widgets(category_tab)

    def create_add_record_widgets(self, parent):
        # Date selection
        ttk.Label(parent, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.date_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))  # Set current date as default
        self.date_entry = ttk.Entry(parent, textvariable=self.date_var)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(parent, text="Select Date", command=self.open_calendar).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Amount
        ttk.Label(parent, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(parent)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Type (Income/Expense)
        ttk.Label(parent, text="Type:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.type_var = tk.StringVar(value="Expense")
        ttk.Radiobutton(parent, text="Expense", variable=self.type_var, value="Expense").grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(parent, text="Income", variable=self.type_var, value="Income").grid(row=2, column=2, padx=5, pady=5, sticky="w")

        # Category
        ttk.Label(parent, text="Category:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(parent, textvariable=self.category_var)
        self.category_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.type_var.trace('w', self.update_categories)
        self.update_categories()

        # Description
        ttk.Label(parent, text="Description:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.description_entry = ttk.Entry(parent)
        self.description_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="we")

        # Recurring
        self.recurring_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Recurring", variable=self.recurring_var).grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Add button
        ttk.Button(parent, text="Add Record", command=self.add_record).grid(row=6, column=0, columnspan=3, padx=5, pady=10)

        # Add a label to display the remaining budget
        self.remaining_budget_label = ttk.Label(parent, text="Remaining Budget: N/A", foreground="white")
        self.remaining_budget_label.grid(row=7, column=0, columnspan=3, padx=5, pady=10)

        # Add button for updating remaining budget
        ttk.Button(parent, text="Update Remaining Budget", command=self.update_remaining_budget).grid(row=8, column=0, columnspan=3, padx=5, pady=10)

    def create_view_records_widgets(self, parent):
        # Create a notebook for income and expense tabs
        view_notebook = ttk.Notebook(parent)
        view_notebook.grid(sticky=tk.NSEW, padx=10, pady=10)

        # Frame for date range selection (moved outside)
        date_frame = ttk.Frame(parent)
        date_frame.grid(padx=10, pady=10, sticky=tk.NSEW)

        # Calculate default start and end dates
        today = date.today()
        first_day_of_month = today.replace(day=1)

        # Start Date
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.start_date_var = tk.StringVar(value=first_day_of_month.strftime("%Y-%m-%d"))  # Set to first of the month
        start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date_var, width=12)
        start_date_entry.grid(row=0, column=1, padx=5)
        ttk.Button(date_frame, text="Select Start Date", command=lambda: self.open_calendar_for_date(self.start_date_var)).grid(row=0, column=2, padx=5)

        # End Date
        ttk.Label(date_frame, text="End Date:").grid(row=1, column=0, padx=5)
        self.end_date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))  # Set to current date
        end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date_var, width=12)
        end_date_entry.grid(row=1, column=1, padx=5)
        ttk.Button(date_frame, text="Select End Date", command=lambda: self.open_calendar_for_date(self.end_date_var)).grid(row=1, column=2, padx=5)

        # Income tab
        income_tab = ttk.Frame(view_notebook)
        view_notebook.add(income_tab, text="Income")
        self.income_tree = self.create_record_view(income_tab, "Income")  # Store reference to income tree

        # Expense tab
        expense_tab = ttk.Frame(view_notebook)
        view_notebook.add(expense_tab, text="Expense")
        self.expense_tree = self.create_record_view(expense_tab, "Expense")  # Store reference to expense tree

        # Add a button for downloading records
        ttk.Button(parent, text="Download Records", command=self.download_records).grid(row=9, column=0, padx=5, pady=10)

        # Add a button for generating records
        ttk.Button(parent, text="Generate", command=self.generate_records).grid(row=10, column=0, padx=5, pady=10)

        # Add a button for editing the selected record
        ttk.Button(parent, text="Edit Selected Record", command=self.edit_selected_record).grid(row=11, column=0, padx=2, pady=2, sticky="w")
        # Add a button for deleting the selected record
        ttk.Button(parent, text="Delete Selected Record", command=self.delete_selected_record).grid(row=11, column=1, padx=2, pady=2, sticky="w")

    def create_record_view(self, parent, record_type):
        # Create a frame to hold the treeview and scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview for displaying records
        tree = ttk.Treeview(tree_frame, columns=("Date", "Amount", "Category", "Description", "Recurring"), show="headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.heading("Date", text="Date")
        tree.heading("Amount", text="Amount")
        tree.heading("Category", text="Category")
        tree.heading("Description", text="Description")
        tree.heading("Recurring", text="Recurring")
        tree.pack(fill=tk.BOTH, expand=True)

        # Configure the scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        # Set the title of the treeview based on record_type
        # tree_frame.title(f"{record_type} Records")  # This line causes the error

        # Return the created treeview
        return tree

    def show_records(self, record_type, start_date_var, end_date_var):
        start_date = start_date_var.get()
        end_date = end_date_var.get()
        print(f"Start Date: {start_date}, End Date: {end_date}, Record Type: {record_type}")  # Debug print

        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        tree = self.expense_tree if record_type == "Expense" else self.income_tree
        self.populate_treeview(tree, record_type, start_date, end_date)

    def populate_treeview(self, tree, record_type, start_date, end_date):
        # Convert start_date and end_date to datetime objects
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            return

        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)

        # Check if records are loaded
        records = self.expenses if record_type == "Expense" else self.income
        print(f"Total {record_type} records: {len(records)}")  # Debug print

        # Filter records for the specified date range
        filtered_records = [
            record for record in records
            if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date
        ]

        print(f"Filtered Records for {record_type}: {len(filtered_records)}")  # Debug print

        # Sort records by date in reverse chronological order
        sorted_records = sorted(filtered_records, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)

        # Add records to treeview
        for index, record in enumerate(sorted_records):
            try:
                tree.insert("", tk.END, values=(
                    record["date"],
                    record["amount"],
                    record["category"],
                    record["description"],
                    "Yes" if record["recurring"] else "No"
                ))
            except KeyError as e:
                print(f"Error in {record_type} record {index}: Missing key {e}")
                print(f"Problematic record: {record}")
                messagebox.showwarning("Data Error", f"Some {record_type.lower()} records are missing required fields. Check the console for details.")

    def edit_record(self, tree, record_type):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to edit.")
            return

        item = tree.item(selected_item)
        records = self.expenses if record_type == "Expense" else self.income

        for index, record in enumerate(records):
            if (record["date"] == item['values'][0] and
                record["amount"] == float(item['values'][1]) and
                record["category"] == item['values'][2] and
                record["description"] == item['values'][3]):
                break
        else:
            messagebox.showerror("Error", "Record not found.")
            return

        # Create a new window for editing
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Record")

        # Date
        ttk.Label(edit_window, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        date_var = tk.StringVar(value=record["date"])
        date_entry = ttk.Entry(edit_window, textvariable=date_var)
        date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(edit_window, text="Select Date", command=lambda: self.open_calendar_for_edit(date_var)).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Amount
        ttk.Label(edit_window, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        amount_entry = ttk.Entry(edit_window)
        amount_entry.insert(0, str(record["amount"]))
        amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Category
        ttk.Label(edit_window, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        category_var = tk.StringVar(value=record["category"])
        category_combobox = ttk.Combobox(edit_window, textvariable=category_var)
        category_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        category_combobox['values'] = self.categories["expense"] if record_type == "Expense" else self.categories["income"]

        # Description
        ttk.Label(edit_window, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        description_entry = ttk.Entry(edit_window)
        description_entry.insert(0, record["description"])
        description_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="we")

        # Recurring
        recurring_var = tk.BooleanVar(value=record["recurring"])
        ttk.Checkbutton(edit_window, text="Recurring", variable=recurring_var).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Save button
        ttk.Button(edit_window, text="Save Changes", command=lambda: self.save_edited_record(
            records, index, date_var, amount_entry, record_type, category_var, description_entry, recurring_var, edit_window, tree
        )).grid(row=5, column=0, columnspan=3, padx=5, pady=10)

    def delete_record(self, tree, record_type):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            item = tree.item(selected_item)
            records = self.expenses if record_type == "Expense" else self.income

            for index, record in enumerate(records):
                if (record["date"] == item['values'][0] and
                    record["amount"] == float(item['values'][1]) and
                    record["category"] == item['values'][2] and
                    record["description"] == item['values'][3]):
                    del records[index]
                    if record["recurring"]:
                        self.categories["recurring"][record_type.lower()].remove(record)
                    break
            else:
                messagebox.showerror("Error", "Record not found.")
                return

            self.save_data()
            self.populate_treeview(tree, record_type, self.start_date_var.get(), self.end_date_var.get())  # Ensure the treeview is updated
            messagebox.showinfo("Success", "Record deleted successfully!")

    def load_data(self):
        def load_file(file_path):
            try:
                with open(file_path, "r") as file:
                    data = file.read()
                    # Remove any trailing commas
                    data = re.sub(r',\s*}', '}', data)
                    data = re.sub(r',\s*]', ']', data)
                    # Replace single quotes with double quotes
                    data = data.replace("'", '"')
                    # Parse the data
                    parsed_data = json.loads(data, cls=CustomJSONDecoder)
                    # Normalize keys to lowercase for dictionaries in lists
                    if isinstance(parsed_data, list):
                        return [{k.lower(): v for k, v in item.items()} for item in parsed_data]
                    return parsed_data
            except FileNotFoundError:
                messagebox.showerror("Error", f"{file_path} not found in the finance_data folder.")
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON in {file_path}: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading {file_path}: {str(e)}")
            return None

        self.expenses = load_file(self.expenses_file) or []
        self.income = load_file(self.income_file) or []
        self.categories = load_file(self.categories_file) or {
            "income": [],
            "expense": [],
            "spending_limits": {},
            "recurring": {
                "income": [],
                "expense": []
            }
        }

        if not all([self.expenses, self.income, self.categories]):
            messagebox.showwarning("Data Loading Issue", "Some data couldn't be loaded. The application might not work as expected.")


    def open_calendar_for_date(self, date_var):
        top = tk.Toplevel(self.master)
        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=lambda: self.set_date_for_variable(cal, top, date_var)).pack(pady=5)

    def set_date_for_variable(self, cal, top, date_var):
        selected_date = cal.get_date()
        date_var.set(selected_date)
        top.destroy()

    def create_category_management_widgets(self, parent):
        # Income Categories
        ttk.Label(parent, text="Income Categories:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.income_listbox = tk.Listbox(parent, width=30, height=10)
        self.income_listbox.grid(row=1, column=0, padx=5, pady=5)
        self.populate_category_listbox(self.income_listbox, self.categories["income"])

        ttk.Button(parent, text="Add Income Category", command=lambda: self.add_category("income")).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(parent, text="Delete Income Category", command=lambda: self.delete_category("income")).grid(row=3, column=0, padx=5, pady=5)

        # Expense Categories
        ttk.Label(parent, text="Expense Categories:").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.expense_listbox = tk.Listbox(parent, width=30, height=10)
        self.expense_listbox.grid(row=1, column=1, padx=5, pady=5)
        self.populate_category_listbox(self.expense_listbox, self.categories["expense"])

        ttk.Button(parent, text="Add Expense Category", command=lambda: self.add_category("expense")).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Delete Expense Category", command=lambda: self.delete_category("expense")).grid(row=3, column=1, padx=5, pady=5)

        # Spending Limits
        ttk.Label(parent, text="Spending Limits:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.spending_limit_listbox = tk.Listbox(parent, width=30, height=10)
        self.spending_limit_listbox.grid(row=5, column=0, padx=5, pady=5)
        self.populate_spending_limits()

        ttk.Button(parent, text="Set Spending Limit", command=self.set_spending_limit).grid(row=6, column=0, padx=5, pady=5)
        ttk.Button(parent, text="Delete Spending Limit", command=self.delete_spending_limit).grid(row=7, column=0, padx=5, pady=5)  # Add this line

    def populate_category_listbox(self, listbox, categories):
        listbox.delete(0, tk.END)
        for category in categories:
            listbox.insert(tk.END, category)

    def populate_spending_limits(self):
        self.spending_limit_listbox.delete(0, tk.END)
        for category, limit in self.categories["spending_limits"].items():
            self.spending_limit_listbox.insert(tk.END, f"{category}: ${limit}")

    def add_category(self, category_type):
        new_category = simpledialog.askstring("Add Category", f"Enter new {category_type} category:")
        if new_category:
            self.categories[category_type].append(new_category)
            if category_type == "income":
                self.populate_category_listbox(self.income_listbox, self.categories["income"])
            else:
                self.populate_category_listbox(self.expense_listbox, self.categories["expense"])
            self.save_categories()

    def delete_category(self, category_type):
        if category_type == "income":
            selected = self.income_listbox.curselection()
            if selected:
                index = selected[0]
                del self.categories["income"][index]
                self.populate_category_listbox(self.income_listbox, self.categories["income"])
        else:
            selected = self.expense_listbox.curselection()
            if selected:
                index = selected[0]
                del self.categories["expense"][index]
                self.populate_category_listbox(self.expense_listbox, self.categories["expense"])
        self.save_categories()

    def set_spending_limit(self):
        # Create a new window for setting the spending limit
        limit_window = tk.Toplevel(self.master)
        limit_window.title("Set Spending Limit")

        # Dropdown for selecting category
        ttk.Label(limit_window, text="Select Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        category_var = tk.StringVar()
        category_combobox = ttk.Combobox(limit_window, textvariable=category_var)
        category_combobox['values'] = self.categories["expense"] + self.categories["income"]  # Combine both expense and income categories
        category_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Entry for spending limit
        ttk.Label(limit_window, text="Spending Limit:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        limit_entry = ttk.Entry(limit_window)
        limit_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Button to set the limit
        ttk.Button(limit_window, text="Set Limit", command=lambda: self.save_spending_limit(category_var, limit_entry, limit_window)).grid(row=2, column=0, columnspan=2, padx=5, pady=10)

    def save_spending_limit(self, category_var, limit_entry, limit_window):
        category = category_var.get()
        try:
            limit = float(limit_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the spending limit.")
            return

        if category and limit is not None:
            self.categories["spending_limits"][category] = limit
            self.populate_spending_limits()
            self.save_categories()
            messagebox.showinfo("Success", f"Spending limit for {category} set to ${limit:.2f}.")
            limit_window.destroy()

    def delete_spending_limit(self):
        selected = self.spending_limit_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a spending limit to delete.")
            return

        index = selected[0]
        category = self.spending_limit_listbox.get(index).split(":")[0].strip()

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the spending limit for {category}?"):
            del self.categories["spending_limits"][category]
            self.populate_spending_limits()
            self.save_categories()
            messagebox.showinfo("Success", f"Spending limit for {category} deleted successfully.")

    def save_categories(self):
        with open(self.categories_file, "w") as file:
            json.dump(self.categories, file)
        self.update_categories()

    def update_categories(self, *args):
        if self.type_var.get() == "Expense":
            self.category_combobox['values'] = self.categories["expense"]
        else:
            self.category_combobox['values'] = self.categories["income"]
        self.category_combobox.set('')

    def add_record(self):
        date = self.date_var.get()
        date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        amount = self.amount_entry.get()
        record_type = self.type_var.get()
        category = self.category_var.get()
        description = self.description_entry.get()
        recurring = self.recurring_var.get()

        if not all([date, amount, record_type, category]):
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        record = {
            "amount": amount,
            "category": category,
            "date": date,
            "description": description,
            "recurring": recurring
        }

        if record_type == "Expense":
            self.expenses.append(record)
        else:
            self.income.append(record)

        if recurring:
            self.categories["recurring"][record_type.lower()].append(record)

        self.save_data()

        # Update the treeview based on the record type
        tree = self.expense_tree if record_type == "Expense" else self.income_tree
        self.populate_treeview(tree, record_type, self.start_date_var.get(), self.end_date_var.get())
        messagebox.showinfo("Success", "Record added successfully!")

        # Clear entries
        self.amount_entry.delete(0, tk.END)
        self.category_var.set('')
        self.description_entry.delete(0, tk.END)
        self.recurring_var.set(False)

    def open_calendar_for_edit(self, date_var):
        top = tk.Toplevel(self.master)
        cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=lambda: self.set_date_for_edit(cal, top, date_var)).pack(pady=5)

    def set_date_for_edit(self, cal, top, date_var):
        date_var.set(cal.get_date())
        top.destroy()

    def save_edited_record(self, records, index, date_var, amount_entry, record_type, category_var, description_entry, recurring_var, edit_window, tree):
        try:
            amount = float(amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        new_record = {
            "date": date_var.get(),
            "amount": amount,
            "category": category_var.get(),
            "description": description_entry.get(),
            "recurring": recurring_var.get()
        }

        old_record = records[index]
        records[index] = new_record

        # Update recurring records if necessary
        if old_record["recurring"] and not new_record["recurring"]:
            self.categories["recurring"][record_type.lower()].remove(old_record)
        elif not old_record["recurring"] and new_record["recurring"]:
            self.categories["recurring"][record_type.lower()].append(new_record)
        elif old_record["recurring"] and new_record["recurring"]:
            recurring_index = self.categories["recurring"][record_type.lower()].index(old_record)
            self.categories["recurring"][record_type.lower()][recurring_index] = new_record

        self.save_data()
        self.populate_treeview(tree, record_type, self.start_date_var.get(), self.end_date_var.get())
        messagebox.showinfo("Success", "Record updated successfully!")
        edit_window.destroy()

    def save_data(self):
        with open(self.expenses_file, "w") as file:
            json.dump(self.expenses, file, indent=2)

        with open(self.income_file, "w") as file:
            json.dump(self.income, file, indent=2)

        with open(self.categories_file, "w") as file:
            json.dump(self.categories, file, indent=2)

    def open_calendar(self):
        top = tk.Toplevel(self.master)
        cal = Calendar(top, selectmode='day', date_pattern='dd/mm/yyyy')
        cal.pack(padx=10, pady=10)
        ttk.Button(top, text="OK", command=lambda: self.set_date(cal, top)).pack(pady=5)

    def set_date(self, cal, top):
        self.date_var.set(cal.get_date())
        top.destroy()


    def create_analysis_widgets(self, parent):
        # Frame for date range selection
        date_frame = ttk.Frame(parent)
        date_frame.grid(padx=10, pady=10, sticky='ew')

        # Calculate default start and end dates
        today = date.today()
        first_day_of_month = today.replace(day=1)

        # Start Date
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.analysis_start_date_var = tk.StringVar(value=first_day_of_month.strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(date_frame, textvariable=self.analysis_start_date_var, width=12)
        start_date_entry.grid(row=0, column=1, padx=5)
        ttk.Button(date_frame, text="Select Start Date", command=lambda: self.open_calendar_for_date(self.analysis_start_date_var)).grid(row=0, column=2, padx=5)

        # End Date
        ttk.Label(date_frame, text="End Date:").grid(row=1, column=0, padx=5)
        self.analysis_end_date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(date_frame, textvariable=self.analysis_end_date_var, width=12)
        end_date_entry.grid(row=1, column=1, padx=5)
        ttk.Button(date_frame, text="Select End Date", command=lambda: self.open_calendar_for_date(self.analysis_end_date_var)).grid(row=1, column=2, padx=5)

        # Analysis Type
        ttk.Label(parent, text="Select Analysis Type:").grid(row=2, column=0, pady=5)
        self.analysis_type_var = tk.StringVar()
        analysis_type_combobox = ttk.Combobox(parent, textvariable=self.analysis_type_var)
        analysis_type_combobox['values'] = ("Categories Analysis", "Income vs Spending", "Monthly by Category")
        analysis_type_combobox.grid(row=2, column=1, pady=5)

        # Chart Type Selection
        ttk.Label(parent, text="Select Chart Type:").grid(row=3, column=0, pady=5)
        self.chart_type_var = tk.StringVar()  # Define chart_type_var
        chart_type_combobox = ttk.Combobox(parent, textvariable=self.chart_type_var)
        chart_type_combobox['values'] = ("Bar Chart", "Line Graph", "Area Chart", "Pie Chart")  # Add chart type options
        chart_type_combobox.grid(row=3, column=1, pady=5)

        # Label to display analysis results
        self.analysis_result_label = ttk.Label(parent, text="", wraplength=400, justify="left")
        self.analysis_result_label.grid(row=4, column=0, columnspan=2, pady=10)

        # Button to perform analysis
        ttk.Button(parent, text="Perform Analysis", command=self.perform_analysis).grid(row=5, column=0, columnspan=2, pady=10)


    def perform_analysis(self):
        start_date = self.analysis_start_date_var.get()
        end_date = self.analysis_end_date_var.get()
        analysis_type = self.analysis_type_var.get()
        chart_type = self.chart_type_var.get()

        print(f"Performing analysis from {start_date} to {end_date} with type {analysis_type} and chart {chart_type}")

        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        if analysis_type == "Monthly by Category":
            self.visualize_monthly_by_category(start_date, end_date, chart_type, record_type="Both")
            
        else:
            if analysis_type in ["Income vs Spending"] and not chart_type:
                messagebox.showerror("Error", "Please select a chart type for the selected analysis.")
                return

            try:
                # Convert start_date and end_date to datetime objects
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                # Perform the selected analysis
                if analysis_type == "Categories Analysis":
                    self.analyze_categories(start_date, end_date)
                elif analysis_type == "Income vs Spending":
                    self.visualize_income_vs_spending(start_date, end_date, chart_type)
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid date format: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

    def analyze_categories(self, start_date, end_date):
        # Ensure start_date and end_date are datetime.date objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Initialize dictionaries to hold totals
        spending_totals = {}
        income_totals = {}

        # Aggregate spending and income by category
        for record in self.expenses:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
            if start_date <= record_date <= end_date:
                category = record["category"]
                spending_totals[category] = spending_totals.get(category, 0) + record["amount"]

        for record in self.income:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
            if start_date <= record_date <= end_date:
                category = record["category"]
                income_totals[category] = income_totals.get(category, 0) + record["amount"]

        # Find categories with highest and lowest spending/income
        highest_spending = max(spending_totals, key=spending_totals.get, default=None)
        lowest_spending = min(spending_totals, key=spending_totals.get, default=None)
        highest_income = max(income_totals, key=income_totals.get, default=None)
        lowest_income = min(income_totals, key=income_totals.get, default=None)

        # Prepare result text
        result_text = (
            f"Highest Spending Category: {highest_spending} with ${spending_totals.get(highest_spending, 0):.2f}\n"
            f"Lowest Spending Category: {lowest_spending} with ${spending_totals.get(lowest_spending, 0):.2f}\n"
            f"Highest Income Category: {highest_income} with ${income_totals.get(highest_income, 0):.2f}\n"
            f"Lowest Income Category: {lowest_income} with ${income_totals.get(lowest_income, 0):.2f}"
        )

        # Update the label with the analysis results
        self.analysis_result_label.config(text=result_text)  # Update the label instead of showing a message box
        
    def visualize_income_vs_spending(self, start_date, end_date, chart_type):
        # Filter data based on the date range
        filtered_income = [record for record in self.income if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date]
        filtered_spending = [record for record in self.expenses if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date]

        # Aggregate data by month
        income_totals = {}
        spending_totals = {}

        for record in filtered_income:
            month = datetime.strptime(record["date"], "%Y-%m-%d").strftime("%Y-%m")
            income_totals[month] = income_totals.get(month, 0) + record["amount"]

        for record in filtered_spending:
            month = datetime.strptime(record["date"], "%Y-%m-%d").strftime("%Y-%m")
            spending_totals[month] = spending_totals.get(month, 0) + record["amount"]

        # Sort months
        months = sorted(set(income_totals.keys()).union(spending_totals.keys()))

        # Prepare data for plotting
        income_values = [income_totals.get(month, 0) for month in months]
        spending_values = [spending_totals.get(month, 0) for month in months]

        # Create a new Toplevel window for the graph
        graph_window = tk.Toplevel(self.master)
        graph_window.title("Income vs Spending Graph")

        # Create a new figure
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Plot data based on the selected chart type
        if chart_type == "Bar Chart":
            x = np.arange(len(months))  # the label locations
            width = 0.35  # the width of the bars

            ax.bar(x - width/2, income_values, width, label='Income', color='green')
            ax.bar(x + width/2, spending_values, width, label='Spending', color='red')

            ax.set_xticks(x)
            ax.set_xticklabels(months)

        elif chart_type == "Line Graph":
            ax.plot(months, income_values, label='Income', color='green')
            ax.plot(months, spending_values, label='Spending', color='red')
        elif chart_type == "Area Chart":
            ax.fill_between(months, income_values, label='Income', color='green', alpha=0.5)
            ax.fill_between(months, spending_values, label='Spending', color='red', alpha=0.5)
        elif chart_type == "Pie Chart":
            # Pie chart needs a single set of values, so we sum across months
            total_income = sum(income_values)
            total_spending = sum(spending_values)
            ax.pie([total_income, total_spending], labels=['Income', 'Spending'], autopct='%1.1f%%', colors=['green', 'red'])
            ax.set_title('Income vs Spending')
            # No need for further configuration for pie chart
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            return  # Exit early for pie chart

        ax.set_title('Income vs Spending')
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount')
        ax.legend()

        # Display the figure in the new window
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Debugging: Confirm the canvas is packed
        print("Graph displayed in the pop-up window.")

    def visualize_monthly_by_category(self, start_date, end_date, chart_type, record_type="Both"):
        # Ensure start_date and end_date are datetime.date objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Aggregate data by month and category
        months = sorted(set(
            datetime.strptime(record["date"], "%Y-%m-%d").strftime("%Y-%m")
            for record in self.expenses + self.income
            if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date
        ))
        
        monthly_data = {month: {} for month in months}
        
        if record_type in ["Income", "Both"]:
            for record in self.income:
                record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
                if start_date <= record_date <= end_date:
                    month = record_date.strftime("%Y-%m")
                    category = record["category"]
                    monthly_data[month][category] = monthly_data[month].get(category, 0) + record["amount"]

        if record_type in ["Expense", "Both"]:
            for record in self.expenses:
                record_date = datetime.strptime(record["date"], "%Y-%m-%d").date()
                if start_date <= record_date <= end_date:
                    month = record_date.strftime("%Y-%m")
                    category = record["category"]
                    monthly_data[month][category] = monthly_data[month].get(category, 0) + record["amount"]

        # Prepare data for plotting
        all_categories_income = sorted(set(category for month in monthly_data.values() for category in month.keys() if category in self.categories["income"]))
        all_categories_expense = sorted(set(category for month in monthly_data.values() for category in month.keys() if category in self.categories["expense"]))

        # Create a new Toplevel window for category selection and graph
        selection_window = tk.Toplevel(self.master)
        selection_window.title("Select Categories for Graph")

        # Listbox for income category selection
        income_listbox_frame = ttk.Frame(selection_window)
        income_listbox_frame.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(income_listbox_frame, text="Select Income Categories:").grid(row=0, column=0)
        income_category_listbox = tk.Listbox(income_listbox_frame, selectmode=tk.MULTIPLE, height=15)
        income_category_listbox.grid(row=1, column=0, sticky="nsew")

        for category in all_categories_income:
            income_category_listbox.insert(tk.END, category)

        # Listbox for expense category selection
        expense_listbox_frame = ttk.Frame(selection_window)
        expense_listbox_frame.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(expense_listbox_frame, text="Select Expense Categories:").grid(row=0, column=0)
        expense_category_listbox = tk.Listbox(expense_listbox_frame, selectmode=tk.MULTIPLE, height=15)
        expense_category_listbox.grid(row=1, column=0, sticky="nsew")

        for category in all_categories_expense:
            expense_category_listbox.insert(tk.END, category)

        # Button to confirm selection and show graph
        def show_selected_graph():
            selected_income_indices = income_category_listbox.curselection()
            selected_income_categories = [income_category_listbox.get(i) for i in selected_income_indices]

            selected_expense_indices = expense_category_listbox.curselection()
            selected_expense_categories = [expense_category_listbox.get(i) for i in selected_expense_indices]

            # Create a new Toplevel window for the graph
            graph_window = tk.Toplevel(selection_window)
            graph_window.title("Monthly by Category Graph")

            # Create a new figure
            fig = Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Prepare data for the selected income categories
            income_values = []
            for category in selected_income_categories:
                total = sum(monthly_data[month].get(category, 0) for month in months)
                income_values.append(total)

            # Prepare data for the selected expense categories
            expense_values = []
            for category in selected_expense_categories:
                total = sum(monthly_data[month].get(category, 0) for month in months)
                expense_values.append(total)

            # Check if there are values to plot
            if not any(income_values) and not any(expense_values):
                messagebox.showwarning("Warning", "No data available for the selected categories.")
                return

            # Plot data based on the selected chart type
            if chart_type == "Pie Chart":
                # Combine income and expense values for pie chart
                total_income = sum(income_values)
                total_expense = sum(expense_values)
                labels = selected_income_categories + selected_expense_categories
                sizes = income_values + expense_values

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            else:
                x = np.arange(len(months))  # the label locations
                width = 0.35  # the width of the bars

                # Plot income categories
                for i, category in enumerate(selected_income_categories):
                    ax.bar(x - width/2, [monthly_data[month].get(category, 0) for month in months], width, label=category)

                # Plot expense categories
                for i, category in enumerate(selected_expense_categories):
                    ax.bar(x + width/2, [monthly_data[month].get(category, 0) for month in months], width, label=category)

            ax.set_xlabel('Month')
            ax.set_ylabel('Amount')
            ax.set_title('Monthly Income and Expense by Category')
            ax.legend()

            # Display the figure in the new window
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        show_graph_button = ttk.Button(selection_window, text="Show Graph", command=show_selected_graph)
        show_graph_button.grid(row=2, column=0, columnspan=2, pady=10)  # Use grid to place the button below the categories

        # Debugging: Confirm the listbox and button are packed
        print("Category selection window displayed.")


    def update_remaining_budget(self):
        budget_texts = []

        for category, limit in self.categories["spending_limits"].items():
            spent = sum(
                record["amount"] for record in self.expenses
                if record["category"] == category and
                datetime.strptime(record["date"], "%Y-%m-%d").month == datetime.now().month
            )
            remaining = limit - spent

            if remaining < 0:
                budget_texts.append(f"{category}: {spent}/{limit} (Exceeded by {-remaining})")
            else:
                budget_texts.append(f"{category}: {spent}/{limit} ({remaining} remaining)")

        if not budget_texts:
            budget_texts.append("No spending limits set.")

        # Update the label with the remaining budget information
        self.remaining_budget_label.config(text="\n".join(budget_texts))

    def download_records(self):
        # Prompt user to select a format
        format_options = ["CSV", "JSON", "XLSX"]
        selected_format = simpledialog.askstring("Select Format", f"Choose format: {', '.join(format_options)}")

        if selected_format not in format_options:
            messagebox.showerror("Error", "Invalid format selected.")
            return

        # Get the selected date range
        start_date = self.start_date_var.get()  # Updated to use the correct variable
        end_date = self.end_date_var.get()      # Updated to use the correct variable

        if not start_date or not end_date:
            messagebox.showerror("Error", "Please select both start and end dates.")
            return

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {e}")
            return

        # Filter records based on the date range
        filtered_income = [record for record in self.income if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date]
        filtered_expenses = [record for record in self.expenses if start_date <= datetime.strptime(record["date"], "%Y-%m-%d").date() <= end_date]

        # Debugging: Print filtered records
        print(f"Filtered Income Records: {filtered_income}")
        print(f"Filtered Expense Records: {filtered_expenses}")

        # Export records based on the selected format
        try:
            if selected_format == "XLSX":
                output_file = os.path.join(self.base_dir, "records.xlsx")
                print(f"Exporting to: {output_file}")  # Debugging: Print the output file path
                with pd.ExcelWriter(output_file) as writer:
                    if filtered_income:
                        pd.DataFrame(filtered_income).to_excel(writer, sheet_name="Income", index=False)
                        print("Income records exported.")  # Debugging: Confirm income export
                    if filtered_expenses:
                        pd.DataFrame(filtered_expenses).to_excel(writer, sheet_name="Expenses", index=False)
                        print("Expense records exported.")  # Debugging: Confirm expense export
                messagebox.showinfo("Success", f"Records exported to {output_file} successfully.")

            elif selected_format == "CSV":
                income_file = os.path.join(self.base_dir, "income_records.csv")
                expenses_file = os.path.join(self.base_dir, "expense_records.csv")
                print(f"Exporting Income to: {income_file}")  # Debugging: Print the output file path
                print(f"Exporting Expenses to: {expenses_file}")  # Debugging: Print the output file path
                
                if filtered_income:
                    pd.DataFrame(filtered_income).to_csv(income_file, index=False)
                    print("Income records exported to CSV.")  # Debugging: Confirm income export
                else:
                    print("No income records to export to CSV.")
                    
                if filtered_expenses:
                    pd.DataFrame(filtered_expenses).to_csv(expenses_file, index=False)
                    print("Expense records exported to CSV.")  # Debugging: Confirm expense export
                else:
                    print("No expense records to export to CSV.")
                    
                messagebox.showinfo("Success", "Records exported to CSV successfully.")

            elif selected_format == "JSON":
                output_file = os.path.join(self.base_dir, "records.json")
                print(f"Exporting to: {output_file}")  # Debugging: Print the output file path
                
                combined_records = {
                    "income": filtered_income,
                    "expenses": filtered_expenses
                }
                with open(output_file, "w") as json_file:
                    json.dump(combined_records, json_file, indent=2)
                    print("Records exported to JSON.")  # Debugging: Confirm JSON export
                
                messagebox.showinfo("Success", f"Records exported to {output_file} successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export records: {str(e)}")

    def generate_records(self):
        # Get the selected date range
        start_date = self.start_date_var.get()
        end_date = self.end_date_var.get()

        # Print the records for debugging
        print(f"Generating records from {start_date} to {end_date}")

        # Call the show_records method to update the records
        self.show_records("Income", self.start_date_var, self.end_date_var)  # Update income records
        self.show_records("Expense", self.start_date_var, self.end_date_var)  # Update expense records
        # You can also add any additional logic here if needed

    def edit_selected_record(self):
        selected_income = self.income_tree.selection()
        selected_expense = self.expense_tree.selection()

        if selected_income:
            self.edit_record(self.income_tree, "Income")
        elif selected_expense:
            self.edit_record(self.expense_tree, "Expense")
        else:
            messagebox.showerror("Error", "Please select a record to edit.")

    def delete_selected_record(self):
        selected_income = self.income_tree.selection()
        selected_expense = self.expense_tree.selection()

        if selected_income:
            self.delete_record(self.income_tree, "Income")
        elif selected_expense:
            self.delete_record(self.expense_tree, "Expense")
        else:
            messagebox.showerror("Error", "Please select a record to delete.")

class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        for key, value in obj.items():
            if isinstance(value, str):
                try:
                    obj[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass
        return obj

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()

