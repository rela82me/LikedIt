import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env file
load_dotenv()

# Your Spotify app credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Authenticate
import re

print("Welcome to LikedIt!")
profile_name = input("Enter your profile name (or press Enter for default): ").strip()

cache_path = ".cache"
if profile_name:
    # Sanitize: keep only alphanumeric, dashes, underscores
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '', profile_name)
    if safe_name:
        cache_path = f".cache-{safe_name}"
        print(f"Using profile: {safe_name}")
    else:
        print("Invalid characters in profile name. Using default profile.")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read playlist-modify-public playlist-modify-private",
    cache_path=cache_path,
    open_browser=True,
    show_dialog=True
))

print("Fetching your Liked Songs...")

# Get all liked songs (paginated)
liked_tracks = []
offset = 0
try:
    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        if not results['items']:
            break
        liked_tracks.extend([item['track']['uri'] for item in results['items']])
        offset += 50
        print(f"Fetched {len(liked_tracks)} songs so far...")
except spotipy.exceptions.SpotifyException as e:
    if e.http_status == 403 and "user may not be registered" in str(e):
        print("\n\nERROR: Authorization failed because the Spotify App is in 'Development Mode'.")
        print("To fix this:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Open your App settings.")
        print("3. Click 'Users and Access'.")
        print("4. Add the email address associated with this new account.")
        print("5. Try running this script again.\n")
        exit(1)
    else:
        raise e

print(f"\nTotal liked songs: {len(liked_tracks)}")

# Playlist handling
user_id = sp.current_user()['id']
playlist_id = None
playlist_url = None
tracks_to_add = []

while True:
    choice = input("\nDo you want to create a (n)ew playlist or (u)pdate an existing one? ").lower()
    
    if choice == 'n':
        # Create new playlist
        playlist_name = input("What do you want to name the new playlist? ")
        is_public = input("Make it public? (y/n): ").lower() == 'y'
        
        new_playlist = sp.user_playlist_create(
            user_id, 
            playlist_name, 
            public=is_public,
            description="Auto-generated from Liked Songs"
        )
        playlist_id = new_playlist['id']
        playlist_url = new_playlist['external_urls']['spotify']
        tracks_to_add = liked_tracks[:] # All liked tracks for a new playlist
        print(f"\nCreated playlist: {playlist_name}")
        break
        
    elif choice == 'u':
        # Update existing playlist
        print("\nFetching your playlists...")
        playlists = []
        offset = 0
        while True:
            # Get user's playlists (limit 50 per request)
            # Note: specifically asking for the user's editable playlists
            results = sp.current_user_playlists(limit=50, offset=offset)
            if not results['items']:
                break
            
            # Filter for playlists the user can modify (owner or collaborator)
            # Simplification: assuming user wants to add to one of their own owned playlists or where they have simple access
            # For now, just listing all visible playlists. Error handling on add will catch permission issues if any.
            playlists.extend(results['items'])
            offset += 50
            
        if not playlists:
            print("No playlists found.")
            continue
            
        print("\nSelect a playlist to update:")
        for idx, pl in enumerate(playlists, 1):
            print(f"{idx}. {pl['name']} ({pl['tracks']['total']} tracks)")
            
        while True:
            try:
                selection = int(input("\nEnter the number of the playlist: "))
                if 1 <= selection <= len(playlists):
                    selected_playlist = playlists[selection - 1]
                    playlist_id = selected_playlist['id']
                    playlist_url = selected_playlist['external_urls']['spotify']
                    print(f"\nSelected playlist: {selected_playlist['name']}")
                    
                    # Fetch existing tracks from the selected playlist
                    print("Checking for existing tracks...")
                    existing_tracks = set()
                    offset = 0
                    while True:
                        results = sp.playlist_items(playlist_id, fields="items.track.uri,next", offset=offset)
                        if not results['items']:
                            break
                        
                        for item in results['items']:
                            if item['track']: # Handle cases where track might be None (e.g. local files or unavailable)
                                existing_tracks.add(item['track']['uri'])
                                
                        if not results['next']:
                            break
                        offset += len(results['items'])
                    
                    # Filter out duplicates
                    for track in liked_tracks:
                        if track not in existing_tracks:
                            tracks_to_add.append(track)
                            
                    print(f"Found {len(existing_tracks)} existing tracks.")
                    print(f"Adding {len(tracks_to_add)} new tracks (skipped {len(liked_tracks) - len(tracks_to_add)} duplicates).")
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        break
    else:
        print("Invalid choice. Please enter 'n' for new or 'u' for update.")

# Add tracks in batches of 100 (Spotify API limit)
if tracks_to_add:
    print("\nAdding tracks to the top of the playlist...")
    # Create batches
    batches = [tracks_to_add[i:i+100] for i in range(0, len(tracks_to_add), 100)]
    
    # Add batches in reverse order at position 0 to maintain correct order at the top
    for batch in reversed(batches):
        sp.playlist_add_items(playlist_id, batch, position=0)
        print(f"Added batch of {len(batch)} tracks...")
else:
    print("\nNo new tracks to add.")

print(f"\n✓ Done! Playlist URL: {playlist_url}")