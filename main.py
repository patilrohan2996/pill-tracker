import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import math

DB_PATH = "tablet_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tablets (
            name TEXT PRIMARY KEY,
            morning INTEGER,
            afternoon INTEGER,
            night INTEGER,
            strip_size INTEGER,
            strips_owned INTEGER,
            total_stock INTEGER,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

def upsert_tablet(name, morning, afternoon, night, strip_size, strips_owned, last_updated):
    total_stock = strip_size * strips_owned
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tablets (name, morning, afternoon, night, strip_size, strips_owned, total_stock, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            morning=excluded.morning,
            afternoon=excluded.afternoon,
            night=excluded.night,
            strip_size=excluded.strip_size,
            strips_owned=excluded.strips_owned,
            total_stock=excluded.total_stock,
            last_updated=excluded.last_updated
    """, (name, morning, afternoon, night, strip_size, strips_owned, total_stock, last_updated))
    conn.commit()
    conn.close()

def fetch_tablets():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tablets", conn)
    conn.close()
    return df

def delete_tablet(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tablets WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Tablet Tracker", layout="wide")
    st.title("💊 Tablet Tracker & Stock Manager")
    st.write("---")
    init_db()
    df = fetch_tablets()

    if df.empty:
        st.info("No tablets added yet.")
        with st.expander("➕ Add New Tablet"):
            with st.form("add_tablet_form"):
                name = st.text_input("Tablet Name")
                col1, col2, col3 = st.columns(3)
                with col1:
                    morning = st.toggle("Morning")
                with col2:
                    afternoon = st.toggle("Afternoon")
                with col3:
                    night = st.toggle("Night")
                strip_size = st.number_input("Tablets per Strip", min_value=1, step=1)
                strips_owned = st.number_input("Number of Strips Owned", min_value=0, step=1)
                submitted = st.form_submit_button("Add Tablet")
                if submitted and name:
                    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    upsert_tablet(name, int(morning), int(afternoon), int(night), strip_size, strips_owned, last_updated)
                    st.success(f"Tablet '{name}' added successfully!")
                    st.rerun()
    else:
        st.subheader("📋 Current Tablet Stock")
        df["Daily Usage"] = df[["morning", "afternoon", "night"]].sum(axis=1)
        df["last_updated"] = pd.to_datetime(df["last_updated"])
        days_since_added = (pd.Timestamp.today() - df["last_updated"]).dt.days
        df["Days Left"] = ((df["total_stock"] - df["Daily Usage"] * days_since_added) / df["Daily Usage"]).fillna(0).astype(int)

        header_cols = st.columns([3, 1, 1, 1, 2, 1, 1])
        header_cols[0].markdown("**Tablet Name**")
        header_cols[1].markdown("**Total Pills**")
        header_cols[2].markdown("**Strip Size**")
        header_cols[3].markdown("**Daily Usage**")
        header_cols[4].markdown("**Remaining Days**")
        header_cols[5].markdown("**Update**")
        header_cols[6].markdown("**Delete**")

        for i, row in df.iterrows():
            cols = st.columns([3, 1, 1, 1, 2, 1, 1])
            cols[0].markdown(f"**{row['name']}**")
            cols[1].markdown(f"{row['total_stock']} pills")
            cols[2].markdown(f"{row['strip_size']}")
            cols[3].markdown(f"{row['Daily Usage']}")
            cols[4].markdown(f"{row['Days Left']} days")

            if row['Days Left'] <= 30:
                needed_pills = 30 * row['Daily Usage'] - row['total_stock']
                if needed_pills > 0:
                    strips_to_order = math.ceil(needed_pills / row['strip_size'])
                    st.warning(f"⚠️ Consider reordering '{row['name']}' — stock may not last for a full month. You should order at least {strips_to_order} strip(s).")

            with cols[5]:
                if st.button("✏️ Update", key=f"update_btn_{i}"):
                    st.session_state[f"edit_index"] = i
                    st.session_state[f"editing"] = True
                    st.rerun()

            with cols[6]:
                if st.button("🗑️ Delete", key=f"delete_btn_{i}"):
                    st.session_state[f"delete_index"] = i
                    st.session_state[f"confirm_delete"] = True
                    st.rerun()

            if st.session_state.get("editing") and st.session_state.get("edit_index") == i:
                with st.form(f"form_update_{i}"):
                    st.subheader(f"Update {row['name']}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        morning = st.toggle("Morning", value=bool(row["morning"]))
                    with col2:
                        afternoon = st.toggle("Afternoon", value=bool(row["afternoon"]))
                    with col3:
                        night = st.toggle("Night", value=bool(row["night"]))
                    strip_size = st.number_input("Tablets per Strip", value=row["strip_size"], min_value=1, step=1, key=f"strip_{i}")
                    strips_owned = st.number_input("Strips Owned", value=row["strips_owned"], min_value=0, step=1, key=f"strips_{i}")
                    confirm_update = st.checkbox("Confirm update")
                    if st.form_submit_button("Update") and confirm_update:
                        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        upsert_tablet(row['name'], int(morning), int(afternoon), int(night), strip_size, strips_owned, last_updated)
                        st.success(f"Updated {row['name']}")
                        st.session_state[f"editing"] = False
                        st.rerun()

            if st.session_state.get("confirm_delete") and st.session_state.get("delete_index") == i:
                confirm = st.checkbox(f"Confirm delete {row['name']}", key=f"confirm_{i}")
                if confirm:
                    delete_tablet(row['name'])
                    st.success(f"Deleted {row['name']}")
                    st.session_state[f"confirm_delete"] = False
                    st.rerun()

        with st.expander("➕ Add Another Tablet"):
            with st.form("add_new_tablet_form"):
                name = st.text_input("Tablet Name")
                col1, col2, col3 = st.columns(3)
                with col1:
                    morning = st.toggle("Morning")
                with col2:
                    afternoon = st.toggle("Afternoon")
                with col3:
                    night = st.toggle("Night")
                strip_size = st.number_input("Tablets per Strip", min_value=1, step=1, key="new_strip")
                strips_owned = st.number_input("Strips Owned", min_value=0, step=1, key="new_owned")
                submitted = st.form_submit_button("Add Tablet")
                if submitted and name:
                    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    upsert_tablet(name, int(morning), int(afternoon), int(night), strip_size, strips_owned, last_updated)
                    st.success(f"Tablet '{name}' added successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()
