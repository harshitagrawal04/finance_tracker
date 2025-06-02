import os
import json
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Define categories and descriptions
category_descriptions = {
    'Food': [
        'Groceries', 'Restaurant meal', 'Fast food', 'Coffee shop', 'Snacks',
        'Delivery food', 'Specialty food items', 'Farmers market', 'Bakery',
        'Ice cream', 'Food truck', 'Cooking ingredients'
    ],
    'Transportation': [
        'Public transport', 'Car maintenance', 'Parking fees', 'Taxi ride',
        'Fuel', 'Car wash', 'Toll fees', 'Bike repair', 'Car rental',
        'Ride-sharing service', 'Vehicle registration', 'Tire replacement'
    ],
    'Housing': [
        'Rent', 'Mortgage payment', 'Home repairs', 'Furniture', 'Home decor',
        'Cleaning supplies', 'Gardening supplies', 'Property taxes',
        'Home insurance', 'Pest control', 'Home security system'
    ],
    'Utilities': [
        'Electricity bill', 'Gas bill', 'Water bill', 'Internet bill', 'Phone bill',
        'Trash collection', 'Sewer service', 'Cable TV', 'Streaming services'
    ],
    'Entertainment': [
        'Movie tickets', 'Concert tickets', 'Theater show', 'Sports event',
        'Museum entry', 'Amusement park', 'Video games', 'Books', 'Magazine subscription',
        'Hobby supplies', 'Gym membership', 'Vacation expenses'
    ],
    'Healthcare': [
        'Doctor visit', 'Medication', 'Dental checkup', 'Eye exam',
        'Health insurance premium', 'Therapy session', 'Medical equipment',
        'Vitamins and supplements', 'Urgent care visit', 'Specialist consultation'
    ],
    'Education': [
        'Tuition', 'Textbooks', 'School supplies', 'Online course',
        'Language learning app', 'Educational software', 'Tutoring',
        'Professional development seminar', 'Certification exam fees'
    ],
    'Other': [
        'Clothing', 'Shoes', 'Accessories', 'Haircut', 'Pet supplies',
        'Gifts', 'Charity donation', 'Subscription box', 'Office supplies',
        'Postage', 'Banking fees', 'Legal services', 'Tax preparation'
    ]
}

once_per_month_descriptions = [
    'Groceries', 'Parking fees', 'Rent', 'Mortgage payment', 'Property taxes',
    'Home insurance', 'Electricity bill', 'Gas bill', 'Water bill', 'Internet bill',
    'Phone bill', 'Trash collection', 'Sewer service', 'Cable TV', 'Streaming services',
    'Magazine subscription', 'Gym membership', 'Health insurance premium',
    'Therapy session', 'Vitamins and supplements', 'Tuition', 'Language learning app',
    'Educational software', 'Tutoring', 'Pet supplies'
]

# Create a folder for JSON file
folder_name = "expense_data"
os.makedirs(folder_name, exist_ok=True)

# Function to generate a random date within a given month
def random_date(year, month):
    start_date = datetime(year, month, 1)
    end_date = start_date.replace(day=28) + timedelta(days=4)
    end_date = end_date - timedelta(days=end_date.day)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

# Generate data from 01-10-2023 to 31-10-2024
start_date = datetime(2023, 10, 1)
end_date = datetime(2024, 10, 31)
all_expenses = []
monthly_entry_count = defaultdict(int)

current_date = start_date
while current_date <= end_date:
    year = current_date.year
    month = current_date.month
    
    total_expense = 0
    target_expense = random.uniform(135000, 165000)
    used_once_per_month = set()
    
    categories = list(category_descriptions.keys())
    
    entry_count = 0
    while total_expense < target_expense and entry_count < 150:
        category = random.choice(categories)
        description = random.choice(category_descriptions[category])
        
        if description in once_per_month_descriptions:
            if description in used_once_per_month:
                continue
            used_once_per_month.add(description)
        
        amount = min(round(random.uniform(100, 5000), 2), target_expense - total_expense)
        amount = max(100, amount)  # Ensure the minimum amount is 100
        amount = '{:.2f}'.format(amount)  # Ensure amount has exactly 2 decimal places
        total_expense += float(amount)
        date = random_date(year, month).strftime('%Y-%m-%d')
        
        expense = {
            "Amount": amount,
            "Category": category,
            "Date": date,
            "Recurring": "No",
            "Description": description
        }
        all_expenses.append(expense)
        entry_count += 1
    
    monthly_entry_count[f"{year}-{month:02d}"] = entry_count
    
    current_date += timedelta(days=32)
    current_date = current_date.replace(day=1)

# Write all expenses to a single JSON file
file_name = f"{folder_name}/expenses.json"
with open(file_name, 'w') as jsonfile:
    json.dump(all_expenses, jsonfile, indent=2, separators=(',', ':'))

print(f"JSON file with expenses from 01-10-2023 to 31-10-2024 has been generated: '{file_name}'")
print(f"Each month's total expense is approximately 150,000 (±10%) with a maximum of 150 entries.")
print("All expenses have an amount of at least 100.")
print("\nNumber of entries per month:")
for month, count in monthly_entry_count.items():
    print(f"{month}: {count} entries")
