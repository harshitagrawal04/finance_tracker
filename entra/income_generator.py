import os
import json
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Define categories and descriptions
category_descriptions = {
    'Salary': [
        'Monthly Salary', 'Overtime Pay', 'Commission', 'Holiday Pay'
    ],
    'Freelance': [
        'Freelance Project', 'Consulting Fee', 'Contract Work',
        'Freelance Writing', 'Photography Services', 'Graphic Design Work',
        'Web Development Project'
    ],
    'Investments': [
        'Stock Dividends', 'Cryptocurrency Gains', 'Peer-to-Peer Lending',
        'Mutual Fund Returns', 'Bond Interest', 'ETF Dividends',
        'Real Estate Investment Trust (REIT) Dividends'
    ],
    'Rental Income': [
        'Rental Property Income', 'Airbnb Hosting', 'Parking Space Rental',
        'Equipment Rental', 'Storage Unit Rental', 'Vehicle Rental'
    ],
    'Dividends': [
        'Stock Dividends', 'Mutual Fund Dividends', 'ETF Dividends',
        'REIT Dividends', 'Preferred Stock Dividends'
    ],
    'Bonus': [
        'Monthly Bonus', 'Performance Bonus',
    ],
    'Side Hustle': [
        'Online Sales', 'Part-time Job', 'Tutoring', 'Selling Digital Products',
        'Sponsored Content', 'Workshop Earnings', 'Podcast Sponsorship',
        'App Revenue', 'Ebook Sales', 'Webinar Income', 'Patreon Supporters',
        'YouTube Ad Revenue', 'Etsy Shop Sales', 'Uber/Lyft Driving',
        'Fiverr Gigs', 'Dropshipping Profits', 'Domain Flipping', 'Podcast Sponsorship'
    ],
    'Other': [
        'Affiliate Marketing', 'Lottery Winnings',
        'Tax Refund', 'Gift Money',
    ]
}

once_per_month_descriptions = [
    'Monthly Salary', 'Monthly Bonus', 'Overtime Pay', 'Commission',
    'Performance Bonus', 'Holiday Pay', 'Rental Property Income', 
    'Airbnb Hosting', 'Parking Space Rental', 'Equipment Rental', 
    'Storage Unit Rental', 'Vehicle Rental', 'Part-time Job', 'Tutoring',
    'Royalties', 'App Revenue', 'Patreon Supporters', 'YouTube Ad Revenue',
    'Vending Machine Earnings'
]

# Create a folder for JSON file
folder_name = "income_data"
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
all_income = []
monthly_entry_count = defaultdict(int)

current_date = start_date
while current_date <= end_date:
    year = current_date.year
    month = current_date.month
    
    total_income = 0
    target_income = random.uniform(135000, 165000)
    used_once_per_month = set()
    
    categories = list(category_descriptions.keys())
    
    entry_count = 0
    max_entries = random.randint(15, 50)  # Set random number of entries between 15 and 50
    while total_income < target_income and entry_count < max_entries:
        category = random.choice(categories)
        description = random.choice(category_descriptions[category])
        
        if description in once_per_month_descriptions:
            if description in used_once_per_month:
                continue
            used_once_per_month.add(description)
        
        amount = min(round(random.uniform(100, 5000), 2), target_income - total_income)
        amount = '{:.2f}'.format(amount)  # Ensure amount has exactly 2 decimal places
        total_income += float(amount)
        date = random_date(year, month).strftime('%Y-%m-%d')
        
        income_entry = {
            "Amount": float(amount),  # Convert to float
            "Category": category,
            "Date": date,
            "Recurring": "No",
            "Description": description
        }
        all_income.append(income_entry)
        entry_count += 1
        monthly_entry_count[f"{year}-{month:02d}"] += 1
    
    current_date += timedelta(days=32)
    current_date = current_date.replace(day=1)

# Write all income to a single JSON file
file_name = f"{folder_name}/income.json"
with open(file_name, 'w') as jsonfile:
    json.dump(all_income, jsonfile, indent=2)

print(f"JSON file has been generated in the '{folder_name}' folder.")
print(f"Income data generated from 01-10-2023 to 31-10-2024.")
print(f"Each month's total income is approximately 150,000 (±10%) with between 15 and 50 entries.")
print("\nNumber of entries per month:")
for month, count in sorted(monthly_entry_count.items()):
    print(f"{month}: {count} entries")
