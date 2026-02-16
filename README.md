# 🎵 LikedIt - Spotify Library Manager

A collection of Python tools to manage, back up, and analyze your Spotify Liked Songs. 

This project allows you to easily sync your Liked Songs to a dedicated playlist and export your entire library data to Excel for deep analysis.

## ✨ Features

- **LikedIt.py**: 
  - Fetches all Liked Songs from your profile.
  - Create a **new playlist** or **update an existing one**.
  - Intelligent duplicate detection.
  - Supports multiple user profiles.
- **analyze_music.py**:
  - Extracts metadata for Liked Songs, Artists, Top Tracks, and Top Artists.
  - Generates Recently Played history.
  - Exports to a beautifully formatted **Excel (.xlsx)** file.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Spotify Developer Credentials ([Dashboard](https://developer.spotify.com/dashboard))

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rela82me/LikedIt.git
   cd LikedIt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and enter your credentials:
     - `SPOTIFY_CLIENT_ID`
     - `SPOTIFY_CLIENT_SECRET`
     - `SPOTIFY_REDIRECT_URI`

## 🛠️ Usage

### Syncing Liked Songs
```bash
python LikedIt.py
```

### Analyzing Music Data
```bash
python analyze_music.py
```

## 🛡️ Privacy & Security

This project uses a `.env` file to keep your API credentials safe. The included `.gitignore` prevents sensitive files from being uploaded.

## 📄 License

This project is licensed under the **MIT License**.

---
*Created with ❤️ for Spotify power users.*