<div align="center">

# 🛡️ Shield CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Shield** is an AI-powered penetration testing automation framework that combines multiple AI providers (OpenAI GPT-4, Claude, Google Gemini, OpenRouter) with 19 battle-tested security tools to deliver intelligent, adaptive security assessments.

</div>

```
      ███████████████████████
      ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██      ███████╗██╗  ██╗██╗███████╗██╗     ██████╗
      ██▓▓▓▓▓▓▓▓███▓▓▓▓▓▓▓▓██      ██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗
      ██▓▓▓▓▓▓▓█████▓▓▓▓▓▓▓██      ███████╗███████║██║█████╗  ██║     ██║  ██║
      ██▓▓▓█████████████▓▓▓██      ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║
      ██▓▓▓▓▓▓▓█████▓▓▓▓▓▓▓██      ███████║██║  ██║██║███████╗███████╗██████╔╝
      ██▓▓▓▓▓▓▓▓███▓▓▓▓▓▓▓▓██      ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝
       ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██
        ██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██       AI-Powered Pentest Framework
         ███▓▓▓▓▓▓▓▓▓▓▓███
           ███▓▓▓▓▓▓▓███          Providers:  Gemini • GPT-4 • Claude • OpenRouter
             ███▓▓▓███            Features:   19 Tools • Smart Workflows • Multi-Agent
               █████
                                  Shield — Your Digital Armor 🛡️
```

<div align="center">

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

> **⚠️ Legal Disclaimer**
>
> Shield is designed exclusively for **authorized security testing** and educational purposes.
>
> - ✅ **Legal Use**: Authorized penetration testing, security research, educational environments
> - ❌ **Illegal Use**: Unauthorized access, malicious activities, any form of cyber attack
>
> **You are fully responsible for ensuring you have explicit written permission before testing any system.**

---

## 🚀 Features

### 🤖 Multi-Provider AI Intelligence
- **4 AI Providers**: OpenAI (GPT-4o), Anthropic (Claude), Google (Gemini), OpenRouter
- **Multi-Agent Architecture**: Specialized AI agents (Planner, Tool Selector, Analyst, Reporter)
- **Adaptive Testing**: AI adjusts tactics based on discovered vulnerabilities

### 🛠️ 19 Integrated Security Tools
| Category | Tools |
|----------|-------|
| **Network** | Nmap, Masscan |
| **Web Recon** | httpx, WhatWeb, Wafw00f |
| **Subdomains** | Subfinder, Amass, DNSRecon |
| **Vulnerability** | Nuclei, Nikto, SQLMap, WPScan |
| **SSL/TLS** | TestSSL, SSLyze |
| **Discovery** | Gobuster, FFuf, Arjun |
| **Analysis** | XSStrike, GitLeaks |

### 📊 Professional Reports
- **Executive Summaries** for non-technical stakeholders
- **Technical Deep-Dives** with evidence and remediation steps
- **Multiple Formats**: Markdown, HTML, JSON
- **AI Decision Traces** for full transparency

### 🔒 Safety & Compliance
- **Safe Mode**: Prevents destructive tool flags
- **Scope Validation**: Automatic blacklisting of private networks
- **Human-in-the-Loop**: Configurable confirmation prompts
- **Complete Audit Logging**

---

## 📦 Installation

### Prerequisites
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **AI Provider API Key** (at least one):
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Anthropic](https://console.anthropic.com/)
  - [Google AI Studio](https://makersuite.google.com/app/apikey) ← Free tier available
  - [OpenRouter](https://openrouter.ai/keys)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd shield-cli

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install
pip install -e .

# Initialize
python -m cli.main init
```

### Configure API Key

Edit `config/shield.yaml` or use environment variables:

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key"

# Linux/macOS
export GOOGLE_API_KEY="your-api-key"
```

---

## ⚡ Quick Start

```bash
# Check setup
python -m cli.main --help

# View AI provider status
python -m cli.main models

# List available workflows
python -m cli.main workflow list

# Run a web pentest
python -m cli.main workflow run --name web_pentest --target https://example.com

# Quick recon scan
python -m cli.main recon https://example.com

# Generate HTML report from session
python -m cli.main report --session 20260405_080000 --format html

# Switch AI provider
python -m cli.main workflow run --name recon --target example.com --provider openai
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         AI Provider Layer               │
│  (OpenAI, Claude, Gemini, OpenRouter)   │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│       Multi-Agent System                │
│  Planner → Tool Agent → Analyst →      │
│            Reporter                      │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Workflow Engine                    │
│  - Parameter Priority                   │
│  - Evidence Capture                     │
│  - Session Management                   │
└─────────────────────────────────────────┘
                 │
┌─────────────────────────────────────────┐
│      Tool Integration Layer             │
│  (19 Security Tools)                    │
└─────────────────────────────────────────┘
```

---

## 📋 Configuration

Edit `config/shield.yaml`:

```yaml
ai:
  provider: gemini          # openai, claude, gemini, openrouter
  gemini:
    model: gemini-2.5-pro
    api_key: null           # Or set GOOGLE_API_KEY env var

pentest:
  safe_mode: true           # Prevent destructive actions
  require_confirmation: true

output:
  format: markdown          # markdown, html, json
  save_path: ./reports
```

---

## 🐳 Docker

```bash
# Build and run
docker-compose up --build

# Run a scan
docker-compose run shield workflow run --name web_pentest --target example.com
```

---

## 🗺️ Roadmap

| Version | Status | Description |
|---------|--------|-------------|
| **v0.1.0** | ✅ Current | Core framework, 19 tool wrappers, 6 workflows, multi-AI |
| v0.2.0 | 🔜 Next | All 19 tools tested end-to-end, improved error handling |
| v0.5.0 | 📋 Planned | HTML report dashboard, real-time scan progress UI |
| v1.0.0 | 🎯 Goal | Production-ready, Docker optimized, full documentation |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Shield — Your Digital Armor** 🛡️

Made with ❤️ for the security community

</div>
