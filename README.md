# 🎵 Spotify Liked Songs Manager

A collection of Python tools to manage, back up, and analyze your Spotify Liked Songs. 

This project allows you to easily sync your Liked Songs to a dedicated playlist (for sharing or easier access) and export your entire listening history and library data to Excel for deep analysis.

## ✨ Features

- **LikedIt.py**: 
  - Fetches all Liked Songs from your profile.
  - Option to create a **brand new playlist** or **update an existing one**.
  - Intelligent duplicate detection (only adds songs that aren't already there).
  - Supports multiple user profiles with separate cache files.

- **analyze_music.py**:
  - Extracts metadata for Liked Songs, Artist details, Top Tracks, and Top Artists.
  - Generates Recently Played history.
  - Exports everything to a beautifully formatted **Excel (.xlsx)** file with multiple sheets:
    - **Summary Stats**: High-level overview of your library.
    - **Liked Songs**: Every track with technical audio metadata.
    - **Artists**: Genre breakdowns and popularity scores.
    - **Top Tracks/Artists**: Your favorites across 3 time ranges (4 weeks, 6 months, All Time).
    - **Recently Played**: Your most recent 50 tracks.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A Spotify Developer account ([Get it here](https://developer.spotify.com/dashboard))

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
   - Open `.env` and fill in your Spotify Application credentials:
     - `SPOTIFY_CLIENT_ID`
     - `SPOTIFY_CLIENT_SECRET`
     - `SPOTIFY_REDIRECT_URI` (usually `http://127.0.0.1:8888/callback`)

## 🛠️ Usage

### Running the Playlist Syncer
```bash
python LikedIt.py
```
Follow the on-screen prompts to enter your profile name and choose between creating a new playlist or updating an existing one.

### Running the Data Analyzer
```bash
python analyze_music.py
```
This will generate a timestamped Excel file in the project directory with all your Spotify data.

## 🛡️ Privacy & Security

This project uses a `.env` file to keep your API credentials safe. **Never share your `.env` file.** The included `.gitignore` is configured to prevent sensitive files (credentials, cache, and exports) from being uploaded to public repositories.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details. Free for everyone to use, modify, and distribute!

---
*Created with ❤️ for Spotify power users.*