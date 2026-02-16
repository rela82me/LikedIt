import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import time

# Load environment variables from .env file
load_dotenv()

# Your Spotify app credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read user-top-read user-read-recently-played"
))

print("=" * 60)
print("SPOTIFY DATA EXTRACTION - WHAT'S LEFT AFTER THE PURGE")
print("=" * 60)

# ============================================================================
# 1. GET ALL LIKED SONGS + METADATA
# ============================================================================
print("\n[1/5] Fetching Liked Songs metadata...")
liked_songs_data = []
offset = 0

while True:
    results = sp.current_user_saved_tracks(limit=50, offset=offset)
    if not results['items']:
        break
    
    for item in results['items']:
        track = item['track']
        liked_songs_data.append({
            'added_at': item['added_at'],
            'track_id': track['id'],
            'track_name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'artist_ids': ', '.join([artist['id'] for artist in track['artists']]),
            'album_name': track['album']['name'],
            'album_id': track['album']['id'],
            'album_type': track['album']['album_type'],
            'release_date': track['album']['release_date'],
            'total_tracks_on_album': track['album']['total_tracks'],
            'track_number': track['track_number'],
            'disc_number': track['disc_number'],
            'duration_ms': track['duration_ms'],
            'duration_min': round(track['duration_ms'] / 60000, 2),
            'explicit': track['explicit'],
            'popularity': track['popularity'],
            'isrc': track.get('external_ids', {}).get('isrc', 'N/A'),
            'uri': track['uri'],
            'preview_url': track['preview_url'],
            'album_art_url': track['album']['images'][0]['url'] if track['album']['images'] else 'N/A',
            'available_markets_count': len(track.get('available_markets', []))
        })
    
    offset += 50
    print(f"  Fetched {len(liked_songs_data)} songs...")

print(f"✓ Total Liked Songs: {len(liked_songs_data)}")

# ============================================================================
# 2. GET ARTIST DETAILS
# ============================================================================
print("\n[2/5] Fetching artist information...")
unique_artist_ids = set()
for song in liked_songs_data:
    unique_artist_ids.update(song['artist_ids'].split(', '))

artist_data = []
artist_ids_list = list(unique_artist_ids)

for i in range(0, len(artist_ids_list), 50):
    batch = artist_ids_list[i:i+50]
    artists = sp.artists(batch)['artists']
    
    for artist in artists:
        artist_data.append({
            'artist_id': artist['id'],
            'artist_name': artist['name'],
            'genres': ', '.join(artist['genres']) if artist['genres'] else 'N/A',
            'popularity': artist['popularity'],
            'followers': artist['followers']['total'],
            'artist_url': artist['external_urls']['spotify']
        })
    
    print(f"  Fetched {min(i+50, len(artist_ids_list))}/{len(artist_ids_list)} artists...")
    time.sleep(0.1)

print(f"✓ Artist data retrieved")

# ============================================================================
# 3. GET TOP TRACKS & ARTISTS (short/medium/long term)
# ============================================================================
print("\n[3/5] Fetching your Top Tracks and Artists...")

top_tracks_data = []
top_artists_data = []

for time_range, label in [('short_term', 'Last 4 Weeks'), 
                           ('medium_term', 'Last 6 Months'), 
                           ('long_term', 'All Time')]:
    # Top Tracks
    top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)
    for idx, track in enumerate(top_tracks['items']):
        top_tracks_data.append({
            'time_range': label,
            'rank': idx + 1,
            'track_name': track['name'],
            'artists': ', '.join([a['name'] for a in track['artists']]),
            'album': track['album']['name'],
            'popularity': track['popularity'],
            'release_date': track['album']['release_date'],
            'duration_min': round(track['duration_ms'] / 60000, 2),
            'uri': track['uri']
        })
    
    # Top Artists
    top_artists = sp.current_user_top_artists(limit=50, time_range=time_range)
    for idx, artist in enumerate(top_artists['items']):
        top_artists_data.append({
            'time_range': label,
            'rank': idx + 1,
            'artist_name': artist['name'],
            'genres': ', '.join(artist['genres']) if artist['genres'] else 'N/A',
            'popularity': artist['popularity'],
            'followers': artist['followers']['total'],
            'uri': artist['uri']
        })

print(f"✓ Top tracks and artists retrieved")

# ============================================================================
# 4. GET RECENTLY PLAYED
# ============================================================================
print("\n[4/5] Fetching recently played tracks...")
recently_played = sp.current_user_recently_played(limit=50)
recently_played_data = []

for item in recently_played['items']:
    track = item['track']
    # Strip timezone from played_at
    played_at = pd.to_datetime(item['played_at']).tz_localize(None)
    recently_played_data.append({
        'played_at': played_at,
        'track_name': track['name'],
        'artists': ', '.join([a['name'] for a in track['artists']]),
        'album': track['album']['name'],
        'duration_min': round(track['duration_ms'] / 60000, 2),
        'uri': track['uri']
    })

print(f"✓ Recently played retrieved")

# ============================================================================
# 5. SOME QUICK ANALYSIS ON WHAT WE GOT
# ============================================================================
print("\n[5/5] Running basic analysis...")

df_liked = pd.DataFrame(liked_songs_data)
df_artists = pd.DataFrame(artist_data)

# Convert date columns and strip timezone
df_liked['added_at'] = pd.to_datetime(df_liked['added_at']).dt.tz_localize(None)
df_liked['release_year'] = pd.to_datetime(df_liked['release_date'], errors='coerce').dt.year

# Basic stats
summary_stats = {
    'Total Liked Songs': [len(df_liked)],
    'Unique Artists': [len(df_artists)],
    'Unique Albums': [df_liked['album_id'].nunique()],
    'Average Song Duration (min)': [round(df_liked['duration_min'].mean(), 2)],
    'Total Hours of Music': [round(df_liked['duration_min'].sum() / 60, 2)],
    'Explicit Tracks': [df_liked['explicit'].sum()],
    'Explicit %': [round(df_liked['explicit'].sum() / len(df_liked) * 100, 1)],
    'Average Popularity Score': [round(df_liked['popularity'].mean(), 1)],
    'Oldest Song Year': [int(df_liked['release_year'].min()) if df_liked['release_year'].notna().any() else 'N/A'],
    'Newest Song Year': [int(df_liked['release_year'].max()) if df_liked['release_year'].notna().any() else 'N/A']
}

# Top artists by number of liked songs
artist_counts = df_liked['artists'].str.split(', ').explode().value_counts().head(20)
top_artists_by_count = pd.DataFrame({
    'Artist': artist_counts.index,
    'Liked Songs Count': artist_counts.values
})

# Songs by decade
df_liked['decade'] = (df_liked['release_year'] // 10 * 10).astype('Int64')
songs_by_decade = df_liked.groupby('decade').size().reset_index(name='Count')

# Songs by year (top 20 years)
songs_by_year = df_liked.groupby('release_year').size().sort_values(ascending=False).head(20).reset_index(name='Count')
songs_by_year.columns = ['Year', 'Count']

# When you added songs (by month)
df_liked['added_month'] = df_liked['added_at'].dt.to_period('M')
songs_added_by_month = df_liked.groupby('added_month').size().reset_index(name='Songs Added')
songs_added_by_month['added_month'] = songs_added_by_month['added_month'].astype(str)

print(f"✓ Analysis complete")

# ============================================================================
# CREATE DATAFRAMES
# ============================================================================
df_top_tracks = pd.DataFrame(top_tracks_data)
df_top_artists = pd.DataFrame(top_artists_data)
df_recently_played = pd.DataFrame(recently_played_data)
df_summary = pd.DataFrame(summary_stats)

# ============================================================================
# EXPORT TO EXCEL
# ============================================================================
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"spotify_data_export_{timestamp}.xlsx"

print(f"\nExporting to {filename}...")

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    df_summary.to_excel(writer, sheet_name='Summary Stats', index=False)
    df_liked.to_excel(writer, sheet_name='Liked Songs', index=False)
    df_artists.to_excel(writer, sheet_name='Artists', index=False)
    top_artists_by_count.to_excel(writer, sheet_name='Top Artists by Count', index=False)
    songs_by_decade.to_excel(writer, sheet_name='Songs by Decade', index=False)
    songs_by_year.to_excel(writer, sheet_name='Songs by Year', index=False)
    songs_added_by_month.to_excel(writer, sheet_name='Songs Added by Month', index=False)
    df_top_tracks.to_excel(writer, sheet_name='Top Tracks', index=False)
    df_top_artists.to_excel(writer, sheet_name='Top Artists', index=False)
    df_recently_played.to_excel(writer, sheet_name='Recently Played', index=False)

print("\n" + "=" * 60)
print("COMPLETE - SURVIVED THE SPOTIFY API PURGE")
print("=" * 60)
print(f"\n📊 Extracted data for {len(liked_songs_data)} liked songs")
print(f"🎤 Cataloged {len(artist_data)} unique artists")
print(f"📈 Retrieved top tracks/artists across 3 time ranges")
print(f"⏱️  Logged last 50 plays")
print(f"📉 Generated summary statistics and breakdowns")
print(f"\n💾 Saved to: {filename}")
print("\nSpotify killed the fun data, but this is what's left.\n")