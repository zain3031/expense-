import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import os

# Page configuration
st.set_page_config(
    page_title="Business Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
DB_FILE = 'expense_tracker.db'

def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#95A5A6',
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('purchase', 'expense', 'credit')),
            amount REAL NOT NULL,
            date DATE NOT NULL,
            vendor_client TEXT,
            category_id INTEGER,
            payment_method TEXT,
            notes TEXT,
            is_reimbursed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # Recurring transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('purchase', 'expense', 'credit')),
            amount REAL NOT NULL,
            vendor_client TEXT,
            category_id INTEGER,
            payment_method TEXT,
            notes TEXT,
            frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
            start_date DATE NOT NULL,
            next_due_date DATE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    
    # Credits tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credits_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'overdue')),
            paid_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Insert default categories
    cursor.execute("SELECT COUNT(*) FROM categories WHERE user_id IS NULL")
    if cursor.fetchone()[0] == 0:
        default_categories = [
            ('Marketing', '#FF6B6B'),
            ('Software', '#4ECDC4'),
            ('Travel', '#45B7D1'),
            ('Supplies', '#FFA07A'),
            ('Utilities', '#98D8C8'),
            ('Salary', '#F7DC6F'),
            ('Rent', '#BB8FCE'),
            ('Miscellaneous', '#95A5A6')
        ]
        cursor.executemany(
            'INSERT INTO categories (name, color, user_id) VALUES (?, ?, NULL)',
            default_categories
        )
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute(
        'SELECT id, username, email FROM users WHERE username = ? AND password = ?',
        (username, hashed_pw)
    )
    user = cursor.fetchone()
    conn.close()
    
    return user

def register_user(username, email, password):
    """Register new user"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed_pw)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, None

def get_categories(user_id):
    """Get all categories for user"""
    conn = sqlite3.connect(DB_FILE)
    query = 'SELECT id, name, color FROM categories WHERE user_id IS NULL OR user_id = ?'
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def add_transaction(user_id, trans_type, amount, date, vendor, category_id, payment_method, notes, is_reimbursed):
    """Add new transaction"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transactions 
        (user_id, type, amount, date, vendor_client, category_id, payment_method, notes, is_reimbursed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, trans_type, amount, date, vendor, category_id, payment_method, notes, is_reimbursed))
    
    conn.commit()
    conn.close()

def get_transactions(user_id, filters=None):
    """Get transactions with optional filters"""
    conn = sqlite3.connect(DB_FILE)
    
    query = '''
        SELECT 
            t.id, t.type, t.amount, t.date, t.vendor_client,
            c.name as category, c.color as category_color,
            t.payment_method, t.notes, t.is_reimbursed
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]
    
    if filters:
        if filters.get('type'):
            query += ' AND t.type = ?'
            params.append(filters['type'])
        if filters.get('start_date'):
            query += ' AND t.date >= ?'
            params.append(filters['start_date'])
        if filters.get('end_date'):
            query += ' AND t.date <= ?'
            params.append(filters['end_date'])
        if filters.get('category'):
            query += ' AND c.name = ?'
            params.append(filters['category'])
    
    query += ' ORDER BY t.date DESC, t.created_at DESC'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def delete_transaction(transaction_id):
    """Delete a transaction"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()

def get_dashboard_data(user_id, start_date=None, end_date=None):
    """Get dashboard summary data"""
    conn = sqlite3.connect(DB_FILE)
    
    query = '''
        SELECT 
            type,
            SUM(amount) as total,
            COUNT(*) as count
        FROM transactions
        WHERE user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ' GROUP BY type'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_category_breakdown(user_id, start_date=None, end_date=None):
    """Get spending by category"""
    conn = sqlite3.connect(DB_FILE)
    
    query = '''
        SELECT 
            c.name as category,
            c.color,
            SUM(t.amount) as total,
            COUNT(*) as count
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type IN ('purchase', 'expense')
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND t.date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND t.date <= ?'
        params.append(end_date)
    
    query += ' GROUP BY c.name, c.color ORDER BY total DESC'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_monthly_breakdown(user_id):
    """Get monthly income vs expenses"""
    conn = sqlite3.connect(DB_FILE)
    
    query = '''
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type IN ('purchase', 'expense') THEN amount ELSE 0 END) as expenses
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 12
    '''
    
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def add_credit(user_id, client_name, amount, due_date, notes):
    """Add credit/invoice tracking"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO credits_tracking (user_id, client_name, amount, due_date, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, client_name, amount, due_date, notes))
    
    conn.commit()
    conn.close()

def get_credits(user_id, status_filter=None):
    """Get credits with optional status filter"""
    conn = sqlite3.connect(DB_FILE)
    
    query = 'SELECT * FROM credits_tracking WHERE user_id = ?'
    params = [user_id]
    
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
    
    query += ' ORDER BY due_date'
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    # Update overdue status
    if not df.empty:
        today = datetime.now().date()
        overdue_mask = (df['status'] == 'pending') & (pd.to_datetime(df['due_date']).dt.date < today)
        if overdue_mask.any():
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            for idx in df[overdue_mask].index:
                cursor.execute(
                    "UPDATE credits_tracking SET status = 'overdue' WHERE id = ?",
                    (df.loc[idx, 'id'],)
                )
            conn.commit()
            conn.close()
            df.loc[overdue_mask, 'status'] = 'overdue'
    
    return df

def mark_credit_paid(credit_id):
    """Mark credit as paid"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE credits_tracking SET status = 'paid', paid_date = ? WHERE id = ?",
        (datetime.now().date(), credit_id)
    )
    conn.commit()
    conn.close()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Initialize database
init_database()

# Authentication
def login_page():
    """Login and registration page"""
    st.title("💰 Business Expense Tracker")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Welcome Back")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Create Account")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            register = st.form_submit_button("Create Account")
            
            if register:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, user_id = register_user(new_username, new_email, new_password)
                    if success:
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username or email already exists")

# Main app
def main_app():
    """Main application after login"""
    
    # Sidebar
    with st.sidebar:
        st.title(f"👤 {st.session_state.username}")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "💸 Transactions", "🏷️ Categories", "🔄 Recurring", "💳 Credits", "📈 Reports"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    
    # Pages
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "💸 Transactions":
        show_transactions()
    elif page == "🏷️ Categories":
        show_categories()
    elif page == "🔄 Recurring":
        show_recurring()
    elif page == "💳 Credits":
        show_credits()
    elif page == "📈 Reports":
        show_reports()

def show_dashboard():
    """Dashboard page"""
    st.title("📊 Dashboard")
    
    # Date filter
    col1, col2 = st.columns([3, 1])
    with col2:
        period = st.selectbox(
            "Period",
            ["All Time", "This Month", "This Quarter", "This Year"],
            label_visibility="collapsed"
        )
    
    # Calculate date range
    start_date, end_date = None, None
    if period == "This Month":
        start_date = datetime.now().replace(day=1).date()
        end_date = datetime.now().date()
    elif period == "This Quarter":
        month = datetime.now().month
        quarter_start = ((month - 1) // 3) * 3 + 1
        start_date = datetime.now().replace(month=quarter_start, day=1).date()
        end_date = datetime.now().date()
    elif period == "This Year":
        start_date = datetime.now().replace(month=1, day=1).date()
        end_date = datetime.now().date()
    
    # Get data
    summary = get_dashboard_data(st.session_state.user_id, start_date, end_date)
    
    # Calculate totals
    total_income = summary[summary['type'] == 'credit']['total'].sum() if 'credit' in summary['type'].values else 0
    total_expenses = summary[summary['type'].isin(['purchase', 'expense'])]['total'].sum()
    net_profit = total_income - total_expenses
    total_transactions = summary['count'].sum()
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💚 Total Income", f"${total_income:,.2f}")
    with col2:
        st.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
    with col3:
        st.metric(
            "💰 Net Profit/Loss", 
            f"${net_profit:,.2f}",
            delta=f"${net_profit:,.2f}" if net_profit >= 0 else f"-${abs(net_profit):,.2f}"
        )
    with col4:
        st.metric("📝 Transactions", int(total_transactions))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Breakdown")
        monthly_data = get_monthly_breakdown(st.session_state.user_id)
        if not monthly_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Income', x=monthly_data['month'], y=monthly_data['income'], marker_color='#10B981'))
            fig.add_trace(go.Bar(name='Expenses', x=monthly_data['month'], y=monthly_data['expenses'], marker_color='#EF4444'))
            fig.update_layout(barmode='group', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
     st.subheader("Expenses by Category")
    category_data = get_category_breakdown(st.session_state.user_id, start_date, end_date)
    if not category_data.empty:
        # Filter out None values from colors
        colors = [c if c is not None else '#95A5A6' for c in category_data['color'].tolist()]
        
        fig = px.pie(
            category_data, 
            values='total', 
            names='category',
            height=300
        )
        # Update colors after creation
        fig.update_traces(marker=dict(colors=colors))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available")

def show_transactions():
    """Transactions page"""
    st.title("💸 Transactions")
    
    # Add transaction form
    with st.expander("➕ Add New Transaction", expanded=False):
        with st.form("add_transaction"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trans_type = st.selectbox("Type", ["expense", "purchase", "credit"])
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                date = st.date_input("Date", value=datetime.now())
            
            with col2:
                vendor = st.text_input("Vendor/Client")
                categories = get_categories(st.session_state.user_id)
                category = st.selectbox("Category", [""] + categories['name'].tolist())
                category_id = categories[categories['name'] == category]['id'].values[0] if category else None
            
            with col3:
                payment_method = st.selectbox(
                    "Payment Method",
                    ["", "Credit Card", "Debit Card", "E-transfer", "Cash", "Check", "PayPal", "Bank Transfer"]
                )
                notes = st.text_area("Notes", height=100)
                is_reimbursed = st.checkbox("Mark as Reimbursed")
            
            submit = st.form_submit_button("💾 Add Transaction", use_container_width=True)
            
            if submit:
                add_transaction(
                    st.session_state.user_id,
                    trans_type,
                    amount,
                    date,
                    vendor,
                    category_id,
                    payment_method,
                    notes,
                    is_reimbursed
                )
                st.success("Transaction added successfully!")
                st.rerun()
    
    # Filters
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    filters = {}
    
    with col1:
        type_filter = st.selectbox("Type", ["All", "credit", "expense", "purchase"])
        if type_filter != "All":
            filters['type'] = type_filter
    
    with col2:
        categories = get_categories(st.session_state.user_id)
        category_filter = st.selectbox("Category", ["All"] + categories['name'].tolist())
        if category_filter != "All":
            filters['category'] = category_filter
    
    with col3:
        start_date = st.date_input("Start Date", value=None)
        if start_date:
            filters['start_date'] = start_date
    
    with col4:
        end_date = st.date_input("End Date", value=None)
        if end_date:
            filters['end_date'] = end_date
    
    # Get and display transactions
    transactions = get_transactions(st.session_state.user_id, filters if filters else None)
    
    if not transactions.empty:
        # Download button
        csv = transactions.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Display transactions
        for idx, row in transactions.iterrows():
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{row['date']}**")
                
                with col2:
                    color = {'credit': '🟢', 'expense': '🔴', 'purchase': '🟡'}
                    st.write(f"{color.get(row['type'], '⚪')} {row['type'].title()}")
                
                with col3:
                    st.write(row['vendor_client'] if pd.notna(row['vendor_client']) else '-')
                
                with col4:
                    if pd.notna(row['category']):
                        st.markdown(
                            f"<span style='color: {row['category_color']}'>●</span> {row['category']}",
                            unsafe_allow_html=True
                        )
                    else:
                        st.write('-')
                
                with col5:
                    amount_color = '#10B981' if row['type'] == 'credit' else '#EF4444'
                    st.markdown(f"<span style='color: {amount_color}; font-weight: bold'>${row['amount']:,.2f}</span>", unsafe_allow_html=True)
                
                with col6:
                    if st.button("🗑️", key=f"del_{row['id']}"):
                        delete_transaction(row['id'])
                        st.rerun()
                
                st.divider()
    else:
        st.info("No transactions found. Add your first transaction above!")

def show_categories():
    """Categories page"""
    st.title("🏷️ Categories")
    
    st.info("📝 Default categories (with 🔒) cannot be deleted. You can create custom categories below.")
    
    # Add category form
    with st.expander("➕ Add New Category"):
        with st.form("add_category"):
            col1, col2 = st.columns(2)
            with col1:
                cat_name = st.text_input("Category Name")
            with col2:
                cat_color = st.color_picker("Color", "#95A5A6")
            
            if st.form_submit_button("Add Category"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO categories (name, color, user_id) VALUES (?, ?, ?)',
                    (cat_name, cat_color, st.session_state.user_id)
                )
                conn.commit()
                conn.close()
                st.success(f"Category '{cat_name}' added!")
                st.rerun()
    
    # Display categories
    categories = get_categories(st.session_state.user_id)
    
    # Get usage stats
    conn = sqlite3.connect(DB_FILE)
    usage_query = '''
        SELECT category_id, COUNT(*) as count, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND category_id IS NOT NULL
        GROUP BY category_id
    '''
    usage_df = pd.read_sql_query(usage_query, conn, params=(st.session_state.user_id,))
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    
    for idx, row in categories.iterrows():
        usage = usage_df[usage_df['category_id'] == row['id']]
        count = int(usage['count'].values[0]) if not usage.empty else 0
        total = float(usage['total'].values[0]) if not usage.empty else 0
        
        with [col1, col2, col3][idx % 3]:
            with st.container():
                is_default = pd.isna(row['id']) if 'user_id' in categories.columns else True
                
                st.markdown(
                    f"<div style='background-color: {row['color']}20; padding: 15px; border-radius: 10px; border-left: 5px solid {row['color']}'>"
                    f"<h4 style='margin: 0'>{row['name']} {'🔒' if idx < 8 else ''}</h4>"
                    f"<p style='margin: 5px 0 0 0; color: #666'>{count} transactions • ${total:,.2f}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.write("")

def show_recurring():
    """Recurring transactions page"""
    st.title("🔄 Recurring Transactions")
    
    st.info("💡 Set up recurring transactions for subscriptions, rent, payroll, etc. They'll be tracked here for easy reference.")
    
    # Add recurring transaction
    with st.expander("➕ Add Recurring Transaction"):
        with st.form("add_recurring"):
            col1, col2 = st.columns(2)
            
            with col1:
                rec_type = st.selectbox("Type", ["expense", "purchase", "credit"], key="rec_type")
                rec_amount = st.number_input("Amount", min_value=0.01, step=0.01, key="rec_amount")
                rec_vendor = st.text_input("Vendor/Client", key="rec_vendor")
                rec_frequency = st.selectbox(
                    "Frequency",
                    ["daily", "weekly", "monthly", "quarterly", "yearly"],
                    key="rec_freq"
                )
            
            with col2:
                categories = get_categories(st.session_state.user_id)
                rec_category = st.selectbox("Category", [""] + categories['name'].tolist(), key="rec_cat")
                rec_payment = st.selectbox(
                    "Payment Method",
                    ["", "Credit Card", "Debit Card", "E-transfer", "Cash"],
                    key="rec_pay"
                )
                rec_start = st.date_input("Start Date", key="rec_start")
                rec_notes = st.text_area("Notes", key="rec_notes")
            
            if st.form_submit_button("Add Recurring Transaction"):
                cat_id = categories[categories['name'] == rec_category]['id'].values[0] if rec_category else None
                
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO recurring_transactions 
                    (user_id, type, amount, vendor_client, category_id, payment_method, notes, frequency, start_date, next_due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (st.session_state.user_id, rec_type, rec_amount, rec_vendor, cat_id, rec_payment, rec_notes, rec_frequency, rec_start, rec_start))
                conn.commit()
                conn.close()
                
                st.success("Recurring transaction added!")
                st.rerun()
    
    # Display recurring transactions
    conn = sqlite3.connect(DB_FILE)
    recurring_df = pd.read_sql_query('''
        SELECT r.*, c.name as category_name, c.color as category_color
        FROM recurring_transactions r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = ?
        ORDER BY r.next_due_date
    ''', conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not recurring_df.empty:
        for idx, row in recurring_df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{row['vendor_client'] if pd.notna(row['vendor_client']) else 'Unnamed'}**")
                    st.caption(row['frequency'].title())
                
                with col2:
                    color = {'credit': '🟢', 'expense': '🔴', 'purchase': '🟡'}
                    st.write(f"{color.get(row['type'], '⚪')} ${row['amount']:,.2f}")
                
                with col3:
                    st.write(f"Next: {row['next_due_date']}")
                
                with col4:
                    if pd.notna(row['category_name']):
                        st.markdown(
                            f"<span style='color: {row['category_color']}'>●</span> {row['category_name']}",
                            unsafe_allow_html=True
                        )
                
                with col5:
                    status = "🟢 Active" if row['is_active'] else "⏸️ Paused"
                    st.write(status)
                
                st.divider()
    else:
        st.info("No recurring transactions yet. Add one above!")

def show_credits():
    """Credits tracking page"""
    st.title("💳 Credits Tracking")
    
    # Add credit
    with st.expander("➕ Add Credit/Invoice"):
        with st.form("add_credit"):
            col1, col2 = st.columns(2)
            
            with col1:
                credit_client = st.text_input("Client Name")
                credit_amount = st.number_input("Amount", min_value=0.01, step=0.01)
            
            with col2:
                credit_due = st.date_input("Due Date")
                credit_notes = st.text_area("Notes (Invoice #, etc.)")
            
            if st.form_submit_button("Add Credit"):
                add_credit(st.session_state.user_id, credit_client, credit_amount, credit_due, credit_notes)
                st.success("Credit added!")
                st.rerun()
    
    # Filters
    status_filter = st.selectbox("Filter by Status", ["All", "pending", "paid", "overdue"])
    
    # Get credits
    credits = get_credits(
        st.session_state.user_id,
        status_filter if status_filter != "All" else None
    )
    
    # Summary
    if not credits.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pending = credits[credits['status'] == 'pending']['amount'].sum()
            st.metric("⏳ Pending", f"${pending:,.2f}")
        
        with col2:
            paid = credits[credits['status'] == 'paid']['amount'].sum()
            st.metric("✅ Paid", f"${paid:,.2f}")
        
        with col3:
            overdue = credits[credits['status'] == 'overdue']['amount'].sum()
            st.metric("⚠️ Overdue", f"${overdue:,.2f}")
        
        st.divider()
        
        # Display credits
        for idx, row in credits.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{row['client_name']}**")
                
                with col2:
                    st.write(f"${row['amount']:,.2f}")
                
                with col3:
                    st.write(f"Due: {row['due_date']}")
                
                with col4:
                    status_emoji = {'pending': '⏳', 'paid': '✅', 'overdue': '⚠️'}
                    st.write(f"{status_emoji.get(row['status'], '❓')} {row['status'].title()}")
                
                with col5:
                    if row['status'] == 'pending' or row['status'] == 'overdue':
                        if st.button("✓ Paid", key=f"pay_{row['id']}"):
                            mark_credit_paid(row['id'])
                            st.rerun()
                
                if pd.notna(row['notes']):
                    st.caption(f"📝 {row['notes']}")
                
                st.divider()
    else:
        st.info("No credits to track yet.")

def show_reports():
    """Reports page"""
    st.title("📈 Reports & Analytics")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        report_start = st.date_input("Start Date", value=datetime.now().replace(day=1).date())
    with col2:
        report_end = st.date_input("End Date", value=datetime.now().date())
    
    # Get data
    summary = get_dashboard_data(st.session_state.user_id, report_start, report_end)
    transactions = get_transactions(st.session_state.user_id, {'start_date': report_start, 'end_date': report_end})
    category_data = get_category_breakdown(st.session_state.user_id, report_start, report_end)
    
    # Summary
    total_income = summary[summary['type'] == 'credit']['total'].sum() if 'credit' in summary['type'].values else 0
    total_expenses = summary[summary['type'].isin(['purchase', 'expense'])]['total'].sum()
    net_profit = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Income", f"${total_income:,.2f}")
    col2.metric("Expenses", f"${total_expenses:,.2f}")
    col3.metric("Net Profit", f"${net_profit:,.2f}", delta=f"${net_profit:,.2f}")
    
    st.divider()
    
    # Category breakdown
    if not category_data.empty:
        st.subheader("Spending by Category")
        
        fig = px.bar(
            category_data,
            x='category',
            y='total',
            color='category',
            color_discrete_sequence=category_data['color'].tolist(),
            text='total'
        )
        fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(
            category_data[['category', 'count', 'total']].rename(columns={
                'category': 'Category',
                'count': 'Transactions',
                'total': 'Total'
            }),
            hide_index=True,
            use_container_width=True
        )
    
    # Export
    if not transactions.empty:
        csv = transactions.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name=f"expense_report_{report_start}_{report_end}.csv",
            mime="text/csv",
            use_container_width=True
        )

# Main app logic
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
