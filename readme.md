# 🔥 RPWTOOLS - Facebook Auto Share Tool

<div align="center">

![RPWTOOLS Banner](https://img.shields.io/badge/RPWTOOLS-v1.0.2-red?style=for-the-badge&logo=facebook)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)](https://github.com/ryograhhh/zinktoolsx)

**A powerful, feature-rich Facebook automation tool with ZERO DELAYS and maximum speed sharing**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [FAQ](#-faq) • [Support](#-support)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [What's New in v1.0.2](#-whats-new-in-v102)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Sharing Modes](#-sharing-modes)
- [Tips & Tricks](#-tips--tricks)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**RPWTOOLS** is an advanced Facebook automation tool designed to help you efficiently share posts across multiple accounts. With the latest v1.0.2 update, we've achieved **MAXIMUM SPEED** with zero delays, enhanced stability, and fixed all critical bugs!

### Why RPWTOOLS?

- ⚡ **ZERO DELAYS** - Maximum speed sharing with no waiting time
- 🔐 **Secure Cookie Database** - Store unlimited cookies with validation
- 🚀 **Auto Token Renewal** - EAAG tokens refresh every 3 minutes automatically
- 🛡️ **Restriction Detection** - Automatic warning for restricted accounts
- 📊 **Statistics Tracking** - Monitor your sharing activity in real-time
- 🎯 **Two Display Modes** - Minimal (mobile) or Detailed (desktop)
- 💎 **User-Friendly** - Clean, colorful terminal interface
- ✅ **FULLY STABLE** - No crashes, no freezing, no problems!

---

## 🎉 What's New in v1.0.2

### 🔥 MAJOR UPDATES

✨ **ZERO DELAYS SHARING**
- Removed ALL delays for maximum speed performance
- Shares continue instantly without waiting
- Lightning-fast parallel multi-account sharing

🛠️ **BUG FIXES**
- Fixed critical "share_loop() parameter mismatch" error
- Fixed sharing freezing/stopping unexpectedly
- Fixed token renewal detection system
- Fixed asyncio exceptions causing crashes
- Fixed display mode selection issues

⚡ **PERFORMANCE IMPROVEMENTS**
- Smart token renewal every 3 minutes automatically
- Better error recovery - continues sharing even after errors
- Enhanced cookie validation with restriction detection
- Faster EAAG token extraction and conversion
- More accurate share counting and statistics

🎨 **UI ENHANCEMENTS**
- Two display modes: Minimal Counter or Detailed Logs
- Automatic restriction detection when adding cookies
- Real-time warning for restricted accounts
- Professional color-coded success/error messages
- Better progress tracking with live counter

---

## ⚡ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 🚀 **Auto Share NORM** | Share using normal accounts with EAAG tokens at MAXIMUM SPEED |
| 💾 **Cookie Database** | Store and manage unlimited cookies (FREE: 10, MAX: unlimited) |
| 🔑 **Auto Validation** | Automatic cookie validation with restriction detection |
| 📈 **Statistics** | View total shares, cooldowns, and account status |
| 👑 **Admin Panel** | Full management system for administrators |
| 🔄 **Auto Updates** | Keep your tool up-to-date with latest features |

### Advanced Features

- **ZERO DELAYS** - Maximum speed sharing with no waiting time
- **Smart Token Renewal** - Auto-renews EAAG tokens every 3 minutes
- **Restriction Detection** - Warns about restricted accounts before sharing
- **Multi-Account Support** - Run multiple accounts simultaneously in parallel
- **Two Display Modes** - Minimal (mobile-friendly) or Detailed (desktop logs)
- **Plan System** - FREE (10 cookies) and MAX (unlimited cookies) plans
- **Enhanced Error Handling** - Continues sharing even when errors occur
- **Real-Time Progress** - Live success counter and status updates

---

## 💻 Requirements

Before installing RPWTOOLS, make sure you have:

- **Python 3.8+** - The tool requires Python 3.8 or higher
- **Termux** (for Android) or **Linux/Windows** terminal
- **Internet Connection** - Required for API access
- **Facebook Accounts** - Dump accounts recommended (not your main account!)

### Python Packages

The tool will automatically install these dependencies:
- `aiohttp` - For async HTTP requests
- `requests` - For synchronous HTTP requests
- `asyncio` - For concurrent operations
- `bcrypt` - For password hashing
- `jwt` - For authentication tokens

---

## 🚀 Installation

### For Termux (Android)

```bash
# Update packages
pkg update && pkg upgrade -y

# Install Python and Git
pkg install python -y
pkg install git -y

# Clone the repository
git clone https://github.com/ryograhhh/zinktoolsx.git

# Navigate to directory
cd zinktoolsx

# Install dependencies
pip install -r requirements.txt

# Run the tool
python share.py
```

### For Linux/Mac

```bash
# Update system (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install python3 python3-pip git -y

# Clone the repository
git clone https://github.com/ryograhhh/zinktoolsx.git

# Navigate to directory
cd zinktoolsx

# Install dependencies
pip3 install -r requirements.txt

# Run the tool
python3 share.py
```

### For Windows

```powershell
# Install Python from https://www.python.org/downloads/
# Install Git from https://git-scm.com/download/win

# Open Command Prompt or PowerShell and run:
git clone https://github.com/ryograhhh/zinktoolsx.git
cd zinktoolsx
pip install -r requirements.txt
python share.py
```

---

## 📖 Usage Guide

### First Time Setup

1. **Register an Account**
   ```
   Choose option: 02/B (REGISTER)
   Enter your username (minimum 3 characters)
   Enter your password (minimum 6 characters)
   Provide your Facebook link (will be auto-normalized)
   Confirm your country (auto-detected)
   ```

2. **Add Cookies to Database**
   ```
   Choose option: 02/B (MANAGE COOKIES)
   Select: Add Cookie
   Paste your Facebook cookie
   Wait for automatic validation (10-15 seconds)
   System will detect if account is restricted
   ```

3. **Start Sharing**
   ```
   Choose option: 01/A (AUTO SHARE)
   Read the information (3-second countdown)
   Select cookies to use (or ALL)
   Enter the post link or ID
   Choose display mode (Minimal or Detailed)
   Watch the magic happen at MAXIMUM SPEED! ⚡
   ```

---

## 🎯 Sharing Modes

### 🟢 Auto Share - NORM ACCOUNTS (v1.0.2)

**Best for:** All users with normal Facebook accounts

**Features:**
- Uses EAAG tokens (business.facebook.com method)
- **ZERO DELAYS** - Maximum speed sharing
- Auto token renewal every 3 minutes
- Smart error recovery and handling
- Restriction detection and warnings
- Two display modes (Minimal/Detailed)

**Key Improvements:**
- ✅ No crashes or freezing
- ✅ Instant sharing with zero waiting
- ✅ Automatic token refresh
- ✅ Better error handling
- ✅ Real-time progress tracking

**Process:**
1. Reads information (3-second countdown)
2. Selects cookies from database (individual or ALL)
3. Converts cookies to EAAG tokens
4. Validates accounts and detects restrictions
5. Shares continuously at MAXIMUM SPEED
6. Auto-renews tokens every 3 minutes
7. Handles errors and continues sharing

**Display Modes:**

**Minimal Mode** (Best for Mobile)
- Shows only success counter
- Compact single-line display
- Updates in place (no scrolling)
- Perfect for small screens

**Detailed Mode** (Best for Desktop)
- Shows timestamp for each share
- Displays account name and UID
- Shows total success count
- Full error information
- Complete sharing logs

---

## 💡 Tips & Tricks

### 🎯 Best Practices

> **💎 Tip:** Always use dump accounts (not your main Facebook account) to avoid losing important data if accounts get restricted.

> **⚡ Tip:** Use Minimal display mode on mobile devices for better readability and performance.

> **🔄 Tip:** The tool automatically detects and warns about restricted accounts - remove them to improve success rate.

> **📊 Tip:** Check your stats regularly (option 03/C) to monitor total shares and account status.

> **🚀 Tip:** With ZERO DELAYS, you can achieve extremely high share counts - use responsibly!

### 🛡️ Security Tips

- Never share your cookies or tokens with others
- Use strong passwords for your RPWTOOLS account
- Regularly check your cookies for dead/restricted accounts
- Don't run multiple instances simultaneously
- Respect Facebook's rate limits
- Always use dump accounts for safety

### 🚀 Performance Tips

- Remove restricted/dead cookies for better performance
- Use "ALL" option to share with all cookies simultaneously
- Choose Minimal mode for faster display updates
- Keep your cookies fresh (delete inactive ones)
- Upgrade to MAX plan for unlimited cookie storage
- Monitor the auto token renewal messages

---

## ⚠️ Warnings & Important Notes

### 🔴 Critical Warnings

> **⚠️ WARNING:** This tool is for educational purposes. Use responsibly and respect Facebook's Terms of Service.

> **⚠️ WARNING:** Always use dump accounts, NEVER your main Facebook account!

> **⚠️ WARNING:** ZERO DELAYS means very fast sharing - use with caution to avoid mass restrictions.

> **⚠️ WARNING:** Excessive sharing can lead to temporary or permanent account restrictions.

### 📝 Important Notes

> **📌 Note:** Make sure all posts you're sharing are set to PUBLIC visibility.

> **📌 Note:** FREE plan allows 10 cookies max. Upgrade to MAX for unlimited storage.

> **📌 Note:** Cookies expire over time. Remove dead cookies and add fresh ones.

> **📌 Note:** The tool requires a stable internet connection to function properly.

> **📌 Note:** Restricted accounts are detected automatically but may not be able to share.

---

## 🔧 Troubleshooting

### Common Issues & Solutions

<details>
<summary><b>🔴 "Cannot connect to server"</b></summary>

**Solution:**
- Check your internet connection
- Verify the API server is online at https://rpwtools.onrender.com
- Try again in a few minutes
- Check if your firewall is blocking the connection
</details>

<details>
<summary><b>🟡 "Cookie is dead/invalid"</b></summary>

**Solution:**
- Get a fresh cookie from your Facebook account
- Make sure you copied the entire cookie string
- Delete the old cookie and add a new one
- Try using a different browser to get the cookie
- Check if the account is restricted
</details>

<details>
<summary><b>🟠 "Failed to extract EAAG token"</b></summary>

**Solution:**
- Cookie might be expired or invalid
- Account might be restricted/blocked
- Try getting a fresh cookie
- Verify the account can access business.facebook.com
- Check if account has any security restrictions
</details>

<details>
<summary><b>🔵 "Account is RESTRICTED warning"</b></summary>

**Solution:**
- This is a warning, not an error
- Restricted accounts may not be able to share
- Remove the restricted cookie from database
- Use different accounts that are not restricted
- This is why we recommend dump accounts!
</details>

<details>
<summary><b>🟣 "Post ID extraction failed"</b></summary>

**Solution:**
- Make sure you're using a valid Facebook post link
- Try using the post ID directly instead of full URL
- Check if the post is public
- Use format: facebook.com/username/posts/123456789
- Or just use the numeric post ID
</details>

<details>
<summary><b>🟤 "FREE plan limit reached (10 cookies)"</b></summary>

**Solution:**
- You've reached the FREE plan limit of 10 cookies
- Delete unused/dead cookies to free up space
- Or upgrade to MAX plan for unlimited cookies
- Contact admin for plan upgrades
</details>

---

## ❓ FAQ

### General Questions

**Q: Is this tool safe to use?**
A: The tool itself is safe and stable (v1.0.2), but Facebook may restrict accounts that violate their ToS. Always use dump accounts!

**Q: Do I need to pay to use this tool?**
A: The tool is free! FREE plan includes 10 cookie storage. MAX plan offers unlimited cookies (rental: ₱150/month or ₱250/3 months).

**Q: How many cookies can I add?**
A: FREE plan: 10 cookies max. MAX plan: Unlimited cookies.

**Q: What does "ZERO DELAYS" mean?**
A: It means shares happen instantly without any waiting time between them - maximum speed performance!

**Q: Why do I see restriction warnings?**
A: The tool automatically detects restricted accounts when you add cookies. This helps you know which accounts might not work.

### Technical Questions

**Q: How do I get my Facebook cookie?**
A: 
1. Open Facebook in your browser
2. Press F12 to open Developer Tools
3. Go to Application/Storage > Cookies
4. Find facebook.com and copy all cookie values
5. Or use a cookie exporter extension

**Q: What are EAAG tokens?**
A: EAAG tokens are access tokens extracted from business.facebook.com. They're more stable than regular tokens and auto-renew.

**Q: How often do tokens renew?**
A: Tokens automatically renew every 3 minutes during active sharing sessions.

**Q: Can I run this 24/7?**
A: Technically yes, but not recommended. Take breaks to avoid detection and mass restrictions.

**Q: What's the difference between Minimal and Detailed display?**
A: Minimal shows only success counter (mobile-friendly). Detailed shows full logs with timestamps and account info (desktop-friendly).

**Q: Why was v1.0.2 released?**
A: To fix critical bugs, remove delays for maximum speed, add restriction detection, and improve overall stability.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs** - Open an issue with detailed information
2. **Suggest Features** - Share your ideas for improvements
3. **Submit Pull Requests** - Fix bugs or add features
4. **Improve Documentation** - Help make the docs better
5. **Share Feedback** - Let us know what you think!

### Development Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR_USERNAME/zinktoolsx.git

# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name

# Open a Pull Request
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 RYO GRAHHH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 📞 Contact & Support

### Developer

- **Name:** KEN DRICK
- **GitHub:** [@ryograhhh](https://github.com/ryograhhh)
- **Facebook:** [facebook.com/ryoevisu](https://facebook.com/ryoevisu)

### Support

Need help? Here's how to reach us:

- 📧 **Email:** Open an issue on GitHub
- 💬 **Facebook:** Message us on Facebook
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/ryograhhh/zinktoolsx/issues)
- ⭐ **Feature Requests:** [GitHub Discussions](https://github.com/ryograhhh/zinktoolsx/discussions)

---

## 🌟 Show Your Support

If you find this tool helpful, please consider:

- ⭐ **Star this repository**
- 🍴 **Fork and contribute**
- 📢 **Share with friends**
- 💬 **Leave feedback**
- ☕ **Buy me a coffee** (optional)

---

## 🎉 Acknowledgments

Special thanks to:

- All contributors and testers who helped with v1.0.2
- The Facebook API community
- Python async/await ecosystem
- Everyone who reported bugs and suggested features
- All users who starred this repo ⭐

---

## 📊 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/ryograhhh/zinktoolsx?style=social)
![GitHub forks](https://img.shields.io/github/forks/ryograhhh/zinktoolsx?style=social)
![GitHub issues](https://img.shields.io/github/issues/ryograhhh/zinktoolsx)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ryograhhh/zinktoolsx)

</div>

---

## 📝 Changelog

### Version 1.0.2 (Current) - January 2025

**MAJOR UPDATE - FULLY STABLE RELEASE**

✨ **New Features:**
- ZERO DELAYS - Maximum speed sharing
- Two display modes (Minimal/Detailed)
- Automatic restriction detection
- Enhanced cookie validation

🛠️ **Bug Fixes:**
- Fixed share_loop parameter mismatch error
- Fixed sharing freezing/stopping
- Fixed token renewal system
- Fixed asyncio exceptions
- Fixed display mode selection

⚡ **Improvements:**
- Smart token renewal every 3 minutes
- Better error recovery
- Faster EAAG token extraction
- More accurate statistics
- Real-time progress tracking

### Version 1.0.1 - December 2024

- Initial stable release
- Cookie database system
- Basic auto share functionality
- Admin panel
- Statistics tracking

### Version 1.0.0 - December 2024

- Initial beta release
- Core sharing functionality
- User authentication
- Basic UI

---

## 🔮 Roadmap

### Planned Features

- [ ] Multi-language support (English, Filipino, etc.)
- [ ] Scheduled sharing with timer
- [ ] Custom delay options for cautious users
- [ ] Post analytics and insights
- [ ] Export/Import cookie database
- [ ] Dark/Light theme toggle
- [ ] Mobile app version (Android APK)
- [ ] Discord bot integration
- [ ] Webhook notifications
- [ ] Multiple post sharing queue

### Under Consideration

- [ ] Video post optimization
- [ ] Story sharing support
- [ ] Comment automation
- [ ] React automation
- [ ] Group posting support
- [ ] Proxy support

---

<div align="center">

### 💖 Made with Love by [RYO GRAHHH](https://github.com/ryograhhh)

**If you like this project, don't forget to give it a ⭐!**

---

**🔥 v1.0.2 - FULLY STABLE - ZERO DELAYS - MAXIMUM SPEED 🔥**

**© 2025 RPWTOOLS. All rights reserved.**

[Back to Top](#-rpwtools---facebook-auto-share-tool)

</div>
