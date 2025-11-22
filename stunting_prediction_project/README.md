# Premium Account Manager

A Chrome extension for managing and accessing premium accounts with automatic login capabilities.

## Features

- **Smart Account Grouping**: Automatically groups multiple accounts from the same service
- **Manual Login Support**: Copy credentials for manual login when needed
- **Advanced Search**: Search by app name, email, domain, or any relevant field
- **Modern UI**: Clean, responsive interface with glassmorphism design
- **Cookie Injection**: Automatic cookie-based login for supported services
- **Multi-Account Selection**: Choose between different accounts for the same service

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `toolify-extension` folder
4. The extension will appear in your browser toolbar

## Usage

1. Click the extension icon to open the popup
2. Browse available premium accounts
3. Use the search bar to find specific services (supports multiple keywords)
4. Click on an account to:
   - Automatically login with cookies (if available)
   - View manual login credentials for copy-paste
   - Open the service website

## Search Features

- **Multi-keyword search**: Search with multiple terms (e.g., "netflix premium")
- **Smart matching**: Searches app names, emails, usernames, and domains
- **Keyboard shortcuts**: Press '/' for quick search access
- **Instant results**: Fast, debounced search with real-time filtering

## Account Types

- 🍪 **Cookie Accounts**: Automatic login using stored cookies
- 🔑 **Credential Accounts**: Login with stored username/password
- 📋 **Manual Accounts**: Copy credentials for manual entry
- ✅ **Full Accounts**: Both cookies and credentials available

## Development

The extension consists of:
- `manifest.json` - Extension configuration
- `background.js` - Service worker with account data and logic  
- `modern-popup.html/js/css` - Modern popup interface
- `content.js` - Content script for page interactions

## Version History

- **v1.0.3** - Enhanced search, removed legacy code, renamed to Premium Account Manager
- **v1.0.2** - Added manual login support and multi-account selection
- **v1.0.1** - Initial modern UI with account grouping
- **v1.0.0** - Basic functionality with cookie injection
