
# 💸 Personal Finance Tracker

**A desktop application to manage income, expenses, and visualize financial trends with ease.**

## 🧠 Key Features

- **User-Friendly GUI**: Built with `Tkinter` for an intuitive experience.
- **Data Persistence**: Uses JSON files to store income and expense data locally.
- **Categorization**: Categorize expenses and income for better organization.
- **Calendar Integration**: Select and filter entries by date using `tkcalendar`.
- **Analytics Dashboard**:
  - Pie charts for category-wise spending.
  - Line plots for income and expenses over time.
- **Search & Filter Tools**: Easily find past records.
- **Editable Entries**: Modify or delete previous inputs.

## 🧰 Technologies Used

| Purpose            | Library/Tool               |
|--------------------|----------------------------|
| GUI                | `tkinter`, `ttk`           |
| Calendar Picker    | `tkcalendar`               |
| Data Storage       | `json`, `os`               |
| Data Processing    | `pandas`, `datetime`, `re` |
| Data Visualization | `matplotlib`, `numpy`      |

## 🗃 File Structure

```
finance_tracker.py
finance_data/
├── expenses.json
└── income.json
```

## 🚀 Getting Started

### Requirements

- Python 3.8+
- Libraries:
  - `tkinter`
  - `tkcalendar`
  - `pandas`
  - `matplotlib`
  - `numpy`



## 📌 Usage Notes

- Designed for **single-user local use**.
- All data is saved in the `finance_data` folder automatically.
- Use the calendar widget to filter transactions by date.
- Interactive plots help visualize trends in your finances.

---

Happy tracking! 🧾💰
```
