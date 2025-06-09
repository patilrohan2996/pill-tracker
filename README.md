# 💊 Tablet Tracker App

This Streamlit-based app helps you manage and monitor your daily medication schedule, track stock levels, and plan reorders intelligently based on consumption rates.

## 🔧 Features

- Add tablets with frequency (Morning, Afternoon, Night)
- Track total pills, strips owned, and daily usage
- View remaining stock days (calculated from last update date)
- Get reorder alerts with strip recommendations
- Update and delete tablets with inline controls
- Fully responsive UI built in Streamlit

## 📦 Files Included

- `main.py` – Core Streamlit application logic
- `tablet_data.db` – SQLite database (auto-generated on first run)
- `requirements.txt` – Python dependencies

## 🚀 Deployment on Streamlit Cloud

1. **Push this repo to GitHub**  
   Make sure `main.py` is in the root directory.

2. **Create a new app on [Streamlit Cloud](https://streamlit.io/cloud)**  
   Link it to your GitHub repository.

3. **Set up required packages**  
   Include a `requirements.txt` file with:
   ```text
   streamlit
   pandas

## Launch and use!
The app will automatically create the tablet_data.db in the deployed environment.

## 📝 Usage Notes
  - The app calculates remaining days dynamically based on your last update and daily consumption.
  - Reorder alerts are shown when the stock won't last a full month.
  - Deletion and updates require confirmation to prevent accidental changes.

## ✨ Roadmap (Suggestions)
  - Email or SMS reminders for low stock
  - User login support
  - Export/import CSV capability
