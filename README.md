# Spotify to Rockbox Transfer Tool

This project facilitates the transfer of your favorite Spotify playlists to an iPod running Rockbox OS. It leverages a modified version of the `spotdl` library to ensure compatibility with the Rockbox OS by using `latin1` encoding for album covers, which is necessary because the default `UTF-8` encoding is not supported by Rockbox.

## Features

- **Retrieve Spotify Playlists**: Fetch playlists directly from your Spotify account.
- **Download Songs**: Download tracks from Spotify playlists with correct encoding for Rockbox OS.
- **Transfer to iPod**: Seamlessly transfer music to your iPod running Rockbox OS.
- **Customizable Settings**: Easily configure the tool via a config file.

## Prerequisites

- Python 3.6 or higher.
- A Spotify Developer account for API access.
- An iPod with Rockbox OS installed.

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Configuration

Set up your application with Spotify credentials and specify your iPod's music destination:

1. Create a Spotify app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) to get your client token and secret.
2. Fill in the `config.cfg` file with your credentials and the iPod's music destination path. Example:

    ```cfg
   [DEFAULT]
   client_id = your_spotify_client_id
   client_secret = your_spotify_client_secret
   # Make sure to leave a trailing slash
   path_to_local_playlists = /path/to/your/ipod/music/folder/
    ```

## Vendored `spotdl`

This project uses a vendored version of `spotdl`, which has been modified to use `latin1` encoding for album covers instead of the default `UTF-8`. This modification is crucial to ensure compatibility with Rockbox OS, which does not support the default encoding for album artwork. The custom `spotdl` library is included in the repository, so no additional installation is necessary.

## Usage

Run the application with:

```sh
python main.py
