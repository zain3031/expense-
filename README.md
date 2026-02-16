# 💰 Business Expense Tracker - Streamlit Edition

A complete business expense tracking application built with Python and Streamlit.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.29+-red)

---

## ✨ Features

### 🔐 User Management
- Secure login/registration system
- Password hashing (SHA-256)
- Multi-user support

### 📊 Dashboard
- Real-time statistics
- Income vs Expenses charts
- Category breakdown
- Monthly trends

### 💸 Transactions
- Add/view/delete transactions
- Transaction types: Purchase, Expense, Credit
- Advanced filtering (date, type, category)
- CSV export
- Reimbursement tracking

### 🏷️ Categories
- 8 pre-loaded default categories
- Create custom categories
- Color coding
- Usage statistics

### 🔄 Recurring Transactions
- Track subscriptions
- Multiple frequencies (daily, weekly, monthly, quarterly, yearly)
- Active/inactive status
- Next due date tracking

### 💳 Credits Tracking
- Monitor outstanding payments
- Client management
- Status tracking (Pending/Paid/Overdue)
- Automatic overdue detection

### 📈 Reports & Analytics
- Visual charts (Plotly)
- Date range filtering
- Category breakdown
- CSV export

---

## 🚀 Quick Start

### Option 1: Streamlit Cloud (Easiest - Recommended!)

1. Upload files to GitHub
2. Go to https://share.streamlit.io
3. Deploy in 2 clicks
4. **Done!** ✨

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open browser: `http://localhost:8501`

### Option 3: cPanel Hosting

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

---

## 📋 Requirements

- Python 3.7+
- Streamlit 1.29+
- Pandas 2.1+
- Plotly 5.18+
- SQLite (built-in)

---

## 💾 Database

Uses **SQLite** - a lightweight, serverless database. Perfect for:
- 3-5 concurrent users
- 100,000+ transactions
- No installation required
- Single file storage

Database file: `expense_tracker.db` (auto-created on first run)

---

## 🎯 Use Cases

Perfect for:
- ✅ Small businesses (3-5 users)
- ✅ Freelancers
- ✅ Startups
- ✅ Personal finance tracking
- ✅ Team expense management

---

## 📱 First Time Setup

1. Run the app
2. Click **"Register"** tab
3. Create your account
4. Login and start tracking!

---

## 🔒 Security Features

- Password hashing (SHA-256)
- User data isolation
- Secure session management
- Optional htaccess protection
- Environment-based configuration

---

## 📊 Technology Stack

- **Backend**: Python 3.7+
- **Framework**: Streamlit
- **Database**: SQLite
- **Charts**: Plotly
- **Data Processing**: Pandas

---

## 🎨 Screenshots

### Dashboard
- Real-time statistics
- Visual charts
- Quick insights

### Transactions
- Easy-to-use interface
- Advanced filters
- One-click actions

### Reports
- Beautiful visualizations
- Exportable data
- Date range selection

---

## 📂 Project Structure

```
expense-tracker-streamlit/
├── app.py                   # Main application (900+ lines!)
├── requirements.txt         # Dependencies
├── setup.sh                # Setup script
├── .streamlit/
│   └── config.toml         # Streamlit config
├── DEPLOYMENT_GUIDE.md     # Deployment instructions
├── README.md               # This file
└── expense_tracker.db      # Database (auto-created)
```

---

## 🛠️ Customization

The app is highly customizable:

- **Colors**: Edit `.streamlit/config.toml`
- **Categories**: Add/modify in the app interface
- **Features**: Modify `app.py` (well-commented code)

---

## 🔄 Updates & Maintenance

### Backup Database
```bash
cp expense_tracker.db backup_$(date +%Y%m%d).db
```

### Update App
1. Edit `app.py`
2. Restart Streamlit
3. Changes apply immediately!

---

## 💡 Pro Tips

1. **Deploy on Streamlit Cloud** - Free, easy, no server needed
2. **Use categories wisely** - Pre-loaded defaults cover most cases
3. **Export regularly** - Download CSV backups
4. **Filter transactions** - Find specific expenses quickly
5. **Track recurring** - Never miss a subscription payment

---

## 🆘 Troubleshooting

**App won't start?**
- Check Python version: `python3 --version`
- Reinstall dependencies: `pip install -r requirements.txt`

**Database errors?**
- Check file permissions: `chmod 755 .`
- Delete `expense_tracker.db` and restart (creates new)

**Can't login?**
- Try registering a new account
- Check if database file exists

See **DEPLOYMENT_GUIDE.md** for more solutions.

---

## 📈 Roadmap

Potential future features:
- [ ] PDF report generation
- [ ] Email notifications
- [ ] Multi-currency support
- [ ] Budget planning
- [ ] Receipt OCR
- [ ] Mobile app
- [ ] API integration

---

## 🤝 Contributing

This is a complete, production-ready application. Feel free to:
- Fork and customize
- Add features
- Fix bugs
- Improve UI

---

## 📄 License

Free to use for personal and commercial purposes.

---

## 🎉 Credits

Built with:
- [Streamlit](https://streamlit.io) - Amazing Python framework
- [Plotly](https://plotly.com) - Beautiful charts
- [Pandas](https://pandas.pydata.org) - Data processing
- [SQLite](https://sqlite.org) - Reliable database

---

## 📞 Support

For deployment help, see **DEPLOYMENT_GUIDE.md**

For feature requests, customize the code to your needs!

---

## ⭐ Quick Comparison

### vs Excel
- ✅ Better UI
- ✅ Multi-user
- ✅ Automatic calculations
- ✅ Visual charts
- ✅ Searchable/filterable

### vs Commercial Software
- ✅ Free forever
- ✅ No subscriptions
- ✅ Full control
- ✅ Easy customization
- ✅ Privacy (your data stays with you)

### vs Node.js Version
- ✅ Easier deployment
- ✅ No npm/node_modules issues
- ✅ Single file app
- ✅ Python (easier to learn)
- ✅ No complex setup

---

## 🚀 Get Started Now!

```bash
# 3 commands to get running:
pip install -r requirements.txt
streamlit run app.py
# Open http://localhost:8501
```

**Or deploy to Streamlit Cloud in 5 minutes!**

---

**Happy expense tracking!** 💰📊✨
