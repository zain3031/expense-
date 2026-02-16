# 🚀 Business Expense Tracker - Streamlit Version

## Complete Deployment Guide for cPanel

---

## ✨ What's Included

This is a **complete business expense tracker** built with Python and Streamlit. Features:

✅ **User Authentication** - Login/Register system
✅ **Dashboard** - Real-time statistics and charts
✅ **Transactions** - Add, view, filter, delete transactions
✅ **Categories** - 8 pre-loaded + custom categories with colors
✅ **Recurring Transactions** - Track subscriptions, rent, etc.
✅ **Credits Tracking** - Monitor outstanding payments
✅ **Reports** - Visual analytics and CSV export
✅ **SQLite Database** - Lightweight, no server needed

---

## 📋 Prerequisites

Your cPanel hosting must have:
- ✅ Python 3.7 or higher
- ✅ SSH or Terminal access
- ✅ Ability to open custom ports (or use reverse proxy)

---

## 🎯 Deployment Method 1: Direct Port (Easiest)

This method runs Streamlit on a custom port like `:8501`

### **Step 1: Upload Files to cPanel**

1. **Login to cPanel**
2. Open **File Manager**
3. Navigate to `public_html`
4. Create a new folder: `expense-app`
5. Upload all these files into `expense-app/`:
   - `app.py`
   - `requirements.txt`
   - `setup.sh`
   - `.streamlit/` folder (with config.toml inside)

### **Step 2: Connect via SSH**

**On Windows:**
- Download PuTTY: https://www.putty.org/
- Connect to your server
- Host: `yourdomain.com` or server IP
- Port: 22
- Login with cPanel credentials

**On Mac/Linux:**
```bash
ssh username@yourdomain.com
```

### **Step 3: Navigate to App Directory**

```bash
cd public_html/expense-app
ls -la
```

You should see: `app.py`, `requirements.txt`, `setup.sh`

### **Step 4: Make Setup Script Executable**

```bash
chmod +x setup.sh
```

### **Step 5: Run Setup Script**

```bash
./setup.sh
```

Wait 3-5 minutes for installation.

### **Step 6: Start the Application**

```bash
# Activate virtual environment
source venv/bin/activate

# Start Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### **Step 7: Keep It Running (Background Process)**

```bash
# Install screen or tmux
# Using nohup (simpler)
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &

# Note the process ID
echo $!
```

### **Step 8: Access Your App**

Open browser:
```
http://yourdomain.com:8501
```

**Success!** You should see the login page! 🎉

### **To Stop the App**

```bash
# Find process ID
ps aux | grep streamlit

# Kill the process
kill [PID]
```

---

## 🎯 Deployment Method 2: Subdomain with Reverse Proxy (Professional)

This method gives you: `https://expenses.yourdomain.com` (no port number)

### **Step 1: Create Subdomain**

1. cPanel → **Subdomains**
2. Subdomain: `expenses`
3. Domain: select your main domain
4. Click **Create**

### **Step 2: Upload Files**

1. File Manager → `public_html/expenses/`
2. Delete default files
3. Upload:
   - `app.py`
   - `requirements.txt`  
   - `setup.sh`
   - `.streamlit/` folder

### **Step 3: SSH Setup (Same as Method 1)**

```bash
cd public_html/expenses
chmod +x setup.sh
./setup.sh
```

### **Step 4: Start Streamlit**

```bash
source venv/bin/activate
nohup streamlit run app.py --server.port 8501 --server.address 127.0.0.1 > streamlit.log 2>&1 &
```

Note: We use `127.0.0.1` (localhost only) for security

### **Step 5: Configure Reverse Proxy**

Create `.htaccess` in `public_html/expenses/`:

```apache
RewriteEngine On
RewriteCond %{HTTP:Upgrade} =websocket [NC]
RewriteRule /(.*)           ws://localhost:8501/$1 [P,L]
RewriteCond %{HTTP:Upgrade} !=websocket [NC]
RewriteRule /(.*)           http://localhost:8501/$1 [P,L]

ProxyPreserveHost On
ProxyPass / http://127.0.0.1:8501/
ProxyPassReverse / http://127.0.0.1:8501/
```

### **Step 6: Access Your App**

```
https://expenses.yourdomain.com
```

**No port number needed!** 🎉

---

## 🎯 Deployment Method 3: Streamlit Cloud (Super Easy - Recommended!)

This is the **EASIEST** method - no cPanel needed at all!

### **Step 1: Create GitHub Account**

1. Go to https://github.com
2. Sign up (it's free)
3. Create a new repository: `expense-tracker-streamlit`

### **Step 2: Upload Files to GitHub**

1. In your repository, click **"Add file" → "Upload files"**
2. Upload all files:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
3. Click **"Commit changes"**

### **Step 3: Deploy to Streamlit Cloud**

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `expense-tracker-streamlit`
5. Main file: `app.py`
6. Click **"Deploy"**
7. Wait 2-3 minutes

### **Step 4: Access Your App**

You'll get a URL like:
```
https://your-username-expense-tracker-streamlit.streamlit.app
```

**That's it!** 🚀 Your app is live!

**Benefits:**
- ✅ No cPanel needed
- ✅ Free hosting
- ✅ HTTPS included
- ✅ Auto-updates when you change code
- ✅ No server management

---

## 🔒 Making It Private

### **Option 1: Password Protection (Streamlit Cloud)**

Add this to the top of `app.py`:

```python
import streamlit as st

# Simple password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter Access Code", type="password")
    if st.button("Submit"):
        if password == "YourSecretCode123":  # Change this!
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect code")
    st.stop()

# Rest of your app code continues here...
```

### **Option 2: Obscure URL**

When deploying to Streamlit Cloud, name your app something random:
- `business-internal-2024-xk9p`
- `expense-secure-app-private`

Don't share the URL publicly!

### **Option 3: htaccess (cPanel Method 1 & 2)**

Create `.htaccess` in the app folder:

```apache
AuthType Basic
AuthName "Restricted Access"
AuthUserFile /home/username/.htpasswd
Require valid-user
```

Then in cPanel:
1. Go to **"Directory Privacy"**
2. Select your expense-app folder
3. Enable protection
4. Create username/password

---

## 🛠️ Troubleshooting

### **"Command not found: streamlit"**

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify streamlit is installed
pip list | grep streamlit

# If not installed
pip install -r requirements.txt
```

### **"Port 8501 already in use"**

```bash
# Find what's using the port
lsof -i :8501

# Kill the process
kill [PID]

# Or use a different port
streamlit run app.py --server.port 8502
```

### **"Permission denied"**

```bash
# Make sure you own the files
ls -la

# Fix permissions
chmod +x setup.sh
chmod 755 app.py
```

### **"Can't connect to database"**

The database file `expense_tracker.db` will be created automatically when you first run the app. Make sure the app directory is writable:

```bash
chmod 755 .
```

### **App stops when I close SSH**

Use one of these methods to keep it running:

**Method 1: nohup (simplest)**
```bash
nohup streamlit run app.py --server.port 8501 > streamlit.log 2>&1 &
```

**Method 2: screen**
```bash
screen -S streamlit
streamlit run app.py --server.port 8501
# Press Ctrl+A then D to detach
# Reattach with: screen -r streamlit
```

**Method 3: tmux**
```bash
tmux new -s streamlit
streamlit run app.py --server.port 8501
# Press Ctrl+B then D to detach
# Reattach with: tmux attach -t streamlit
```

---

## 🔄 Updating the App

### **Method 1: Edit via cPanel**

1. File Manager → Navigate to app folder
2. Right-click `app.py` → Edit
3. Make changes
4. Save
5. Restart the app:
   ```bash
   kill [old_process_id]
   streamlit run app.py --server.port 8501
   ```

### **Method 2: Git pull (if using GitHub)**

```bash
cd public_html/expense-app
git pull origin main
# Restart app
```

---

## 📊 Monitoring & Logs

### **View Logs**

```bash
tail -f streamlit.log
```

### **Check if App is Running**

```bash
ps aux | grep streamlit
```

### **Resource Usage**

```bash
top
# Press 'q' to quit
```

---

## 💾 Backup

### **Backup Database**

```bash
# Copy database file
cp expense_tracker.db expense_tracker_backup_$(date +%Y%m%d).db

# Download via cPanel File Manager
```

### **Automated Backup (crontab)**

```bash
crontab -e

# Add this line (daily backup at 2 AM)
0 2 * * * cp /home/username/public_html/expense-app/expense_tracker.db /home/username/backups/expense_$(date +\%Y\%m\%d).db
```

---

## 🎯 Which Method Should You Use?

| Method | Difficulty | URL | Best For |
|--------|-----------|-----|----------|
| **Method 1: Direct Port** | Easy | `domain.com:8501` | Testing, personal use |
| **Method 2: Reverse Proxy** | Medium | `expenses.domain.com` | Professional setup |
| **Method 3: Streamlit Cloud** | Very Easy | `.streamlit.app` | **RECOMMENDED!** |

---

## 🚀 Quick Start (Streamlit Cloud - Fastest!)

1. **Upload files to GitHub** (5 minutes)
2. **Deploy on Streamlit Cloud** (2 minutes)
3. **Access your app** - Done! 🎉

**Total time: 7 minutes!**

---

## 📱 Features You'll Get

Once deployed, you can:

✅ **Register** your account (first user)
✅ **Add transactions** - purchases, expenses, income
✅ **Categorize** with 8 default + custom categories
✅ **Track recurring** - subscriptions, rent, payroll
✅ **Monitor credits** - outstanding payments from clients
✅ **Generate reports** - visual analytics & CSV export
✅ **Filter & search** - find transactions easily
✅ **View dashboard** - real-time statistics

---

## 🎓 First Time Use

After deployment:

1. **Open your app URL**
2. Click **"Register" tab**
3. Create your admin account:
   - Username: `admin`
   - Email: `your@email.com`
   - Password: (min 6 characters)
4. Click **"Create Account"**
5. Login with your credentials
6. **Add your first transaction!**

---

## 💡 Pro Tips

1. **Use Streamlit Cloud** - It's free and easiest!
2. **Backup regularly** - Download your `.db` file weekly
3. **Use strong passwords** - Both for the app and any htaccess
4. **Don't share URL publicly** - Keep it private
5. **Export data often** - Use the CSV download feature

---

## 🆘 Need Help?

**Common Issues:**

1. **Can't access app** → Check firewall/port settings
2. **Database errors** → Check file permissions (755)
3. **App crashes** → Check `streamlit.log` for errors
4. **Slow performance** → Streamlit Cloud has resource limits

---

## 📦 Files Included

```
expense-tracker-streamlit/
├── app.py                    # Main application (all features!)
├── requirements.txt          # Python dependencies
├── setup.sh                 # Installation script
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── DEPLOYMENT_GUIDE.md      # This file
└── expense_tracker.db       # Database (auto-created)
```

---

## 🎉 You're All Set!

Choose your deployment method and get started in minutes!

**Recommended: Start with Streamlit Cloud** - it's free, fast, and requires zero server setup!

---

**Questions?** Just deploy it and start using! The interface is intuitive and self-explanatory! 💪
