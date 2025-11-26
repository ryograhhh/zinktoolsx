# 🔥 RPWTOOLS - Facebook Auto Share Tool

<div align="center">

![RPWTOOLS Banner](https://img.shields.io/badge/RPWTOOLS-v1.0-red?style=for-the-badge&logo=facebook)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](https://github.com/ryograhhh/zinktoolsx)

**A powerful, feature-rich Facebook automation tool for sharing posts with multiple accounts**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [FAQ](#-faq) • [Support](#-support)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
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

**RPWTOOLS** is an advanced Facebook automation tool designed to help you efficiently share posts across multiple accounts and pages. Whether you're managing social media campaigns, promoting content, or just need to share posts quickly, RPWTOOLS has got you covered!

### Why RPWTOOLS?

- ✨ **Two Powerful Sharing Modes** - Choose between PAGE & NORM or NORM ACCOUNTS only
- 🚀 **Maximum Speed** - Zero delays for lightning-fast sharing
- 🔐 **Secure** - Your credentials are safely managed in a database
- 🎯 **Smart Management** - Paired cookie & token system for reliability
- 📊 **Statistics Tracking** - Monitor your sharing activity
- 🔄 **Auto Token Renewal** - Tokens refresh automatically every 5 minutes
- 💎 **User-Friendly** - Clean, colorful terminal interface

---

## ⚡ Features

### Core Features

| Feature | Description |
|---------|-------------|
| 🎭 **Auto Share V1** | Share using both pages and normal accounts with synchronized pausing |
| 🌐 **Auto Share V2** | Share using normal accounts with EAAG tokens (no pages needed) |
| 🔑 **Cookie to Token** | Convert Facebook cookies to access tokens easily |
| 💾 **Database Management** | Store and manage your paired cookies & tokens |
| 📈 **Statistics** | View your total shares, cooldowns, and account status |
| 👑 **Admin Panel** | Full management system for administrators |
| 🔄 **Auto Updates** | Keep your tool up-to-date with latest features |

### Advanced Features

- **Global Pause System** - All accounts pause together when Facebook limits detected
- **Smart Error Handling** - Automatically switches strategies on failure
- **Token Auto-Renewal** - V2 mode renews EAAG tokens every 5 minutes
- **Multi-Account Support** - Run multiple accounts simultaneously
- **Plan System** - FREE, VIP, and MAX plans with different cooldowns
- **Cooldown Management** - Smart cooldown system to prevent bans

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
python rpw.py
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
python3 rpw.py
```

### For Windows

```powershell
# Install Python from https://www.python.org/downloads/
# Install Git from https://git-scm.com/download/win

# Open Command Prompt or PowerShell and run:
git clone https://github.com/ryograhhh/zinktoolsx.git
cd zinktoolsx
pip install -r requirements.txt
python rpw.py
```

---

## 📖 Usage Guide

### First Time Setup

1. **Register an Account**
   ```
   Choose option: 02/B (REGISTER)
   Enter your username (minimum 3 characters)
   Enter your password (minimum 6 characters)
   Provide your Facebook link
   Confirm your country
   ```

2. **Add Paired Accounts**
   ```
   Choose option: 04/D (MANAGE COOKIE & TOKEN)
   Select: Add Account
   Paste your Facebook cookie
   Paste your access token
   ```

3. **Start Sharing**
   ```
   Choose option: 01/A (AUTO SHARE) or 02/B (AUTO SHARE V2)
   Read the warnings carefully
   Enter the post link or ID
   Watch the magic happen! ✨
   ```

---

## 🎯 Sharing Modes

### 🔵 Auto Share V1 - PAGE & NORM

**Best for:** Users with Facebook pages or mixed accounts

**Features:**
- Uses both page tokens and normal account tokens
- Synchronized global pause system
- Maximum speed with zero delays
- Automatic page token extraction

**⚠️ Warning:**
- NOT recommended for video FB posts
- Can quickly limit pages and normal accounts
- Make sure your post is set to PUBLIC
- Read warnings carefully before proceeding

**Process:**
1. Reads warnings (5-second countdown)
2. Confirms with YES/NO prompt
3. Checks cooldown status
4. Loads paired accounts from database
5. Extracts page tokens from accounts
6. Shares continuously until stopped

### 🟢 Auto Share V2 - NORM ACCOUNTS

**Best for:** Users with normal accounts only (no pages)

**Features:**
- Uses EAAG tokens (business.facebook.com method)
- Maximum speed with zero delays
- Auto token renewal every 5 minutes
- Smart error recovery

**ℹ️ Info:**
- Uses EAAG tokens for stability
- Best for accounts without pages
- Tokens auto-renew during sharing
- Make sure your post is PUBLIC

**Process:**
1. Reads information (3-second countdown)
2. Selects cookies from database
3. Converts cookies to EAAG tokens
4. Shares continuously with auto-renewal
5. Handles errors with token refresh

---

## 💡 Tips & Tricks

### 🎯 Best Practices

> **💎 Tip:** Always use dump accounts (not your main Facebook account) to avoid losing important data if accounts get restricted.

> **⚡ Tip:** For video posts, consider using V2 mode as it's generally more stable for video content.

> **🔄 Tip:** If you hit limits, wait for the global pause to expire before trying again. Don't rush!

> **📊 Tip:** Check your stats regularly (option 05/E) to monitor cooldowns and account status.

### 🛡️ Security Tips

- Never share your cookies or tokens with others
- Use strong passwords for your RPWTOOLS account
- Regularly check your paired accounts for dead cookies
- Don't run multiple instances simultaneously
- Respect Facebook's rate limits

### 🚀 Performance Tips

- Use V1 for maximum page reach
- Use V2 for normal account stability
- Keep your cookies fresh (delete dead ones)
- Upgrade to VIP/MAX for lower cooldowns
- Monitor blocked cookies and remove them

---

## ⚠️ Warnings & Important Notes

### 🔴 Critical Warnings

> **⚠️ WARNING:** This tool is for educational purposes. Use responsibly and respect Facebook's Terms of Service.

> **⚠️ WARNING:** Always use dump accounts, NEVER your main Facebook account!

> **⚠️ WARNING:** Video posts may trigger limits faster. Use with caution!

> **⚠️ WARNING:** Excessive sharing can lead to temporary or permanent account restrictions.

### 📝 Important Notes

> **📌 Note:** Make sure all posts you're sharing are set to PUBLIC visibility.

> **📌 Note:** FREE plan has 5-minute cooldowns. Upgrade for faster access.

> **📌 Note:** Cookies and tokens expire. Re-add them if they stop working.

> **📌 Note:** The tool requires a stable internet connection to function properly.

---

## 🔧 Troubleshooting

### Common Issues & Solutions

<details>
<summary><b>🔴 "Cannot connect to server"</b></summary>

**Solution:**
- Check your internet connection
- Verify the API server is online
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
</details>

<details>
<summary><b>🟠 "Cooldown active"</b></summary>

**Solution:**
- Wait for the cooldown timer to expire
- Check your plan limits (FREE: 5min, VIP: 1min, MAX: none)
- Don't spam the share button
- Contact admin for plan upgrades
</details>

<details>
<summary><b>🔵 "Failed to get page tokens"</b></summary>

**Solution:**
- Make sure your account has pages
- Verify your token has page permissions
- Try V2 mode if you don't have pages
- Re-add your cookie and token
</details>

<details>
<summary><b>🟣 "Post ID extraction failed"</b></summary>

**Solution:**
- Make sure you're using a valid Facebook post link
- Try using the post ID directly instead
- Check if the post is public
- Use the full URL format
</details>

---

## ❓ FAQ

### General Questions

**Q: Is this tool safe to use?**
A: The tool itself is safe, but Facebook may restrict accounts that violate their ToS. Always use dump accounts!

**Q: Do I need to pay to use this tool?**
A: The tool is free! However, there are premium plans (VIP/MAX) for lower cooldowns.

**Q: How many accounts can I add?**
A: You can add unlimited paired accounts to your database.

**Q: What's the difference between V1 and V2?**
A: V1 uses pages + normal accounts, V2 uses only normal accounts with EAAG tokens.

### Technical Questions

**Q: How do I get my Facebook cookie?**
A: 
1. Open Facebook in your browser
2. Press F12 to open Developer Tools
3. Go to Application/Storage > Cookies
4. Copy the entire cookie value

**Q: How do I get an access token?**
A: Use the Cookie to Token feature (option 03/C) in the tool!

**Q: Why do my tokens expire?**
A: Facebook tokens expire after some time. V2 mode auto-renews them every 5 minutes.

**Q: Can I run this 24/7?**
A: Not recommended. Take breaks to avoid detection and limits.

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

- All contributors and testers
- The Facebook API community
- Python async/await ecosystem
- Everyone who starred this repo ⭐

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

### Version 1.0 (Current)

- ✨ Initial release
- 🎭 Auto Share V1 (PAGE & NORM)
- 🌐 Auto Share V2 (NORM ACCOUNTS)
- 🔑 Cookie to Token converter
- 💾 Database management system
- 📈 Statistics tracking
- 👑 Admin panel
- 🔄 Auto update feature

---

## 🔮 Roadmap

### Planned Features

- [ ] Multi-language support
- [ ] Scheduled sharing
- [ ] Custom delay options
- [ ] Post analytics
- [ ] Export/Import accounts
- [ ] Dark/Light theme toggle
- [ ] Mobile app version
- [ ] Discord bot integration

---

<div align="center">

### 💖 Made with Love by [RYO GRAHHH](https://github.com/ryograhhh)

**If you like this project, don't forget to give it a ⭐!**

---

**© 2025 RPWTOOLS. All rights reserved.**

[Back to Top](#-rpwtools---facebook-auto-share-tool)

</div>
