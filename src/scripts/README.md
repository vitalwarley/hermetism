# Scripts

This directory contains utility scripts for the Hermetism project.

## YouTube Transcript Downloader

The `youtube_transcript.py` script allows you to download transcripts from YouTube videos and save them to a specified folder.

### Installation

Before using the script, make sure to install the required dependencies:

```bash
pip install -r requirements.txt
```

### Usage

```bash
python youtube_transcript.py --video_id VIDEO_ID --output_folder OUTPUT_FOLDER [--language LANGUAGE]
```

#### Arguments:

- `--video_id`: The YouTube video ID (the part after v= in the URL)
- `--output_folder`: The folder where the transcript will be saved
- `--language`: Optional. The language code for the transcript (default: en)

#### Example:

```bash
# Download transcript for a video in English
python youtube_transcript.py --video_id dQw4w9WgXcQ --output_folder ../../data/transcripts

# Download transcript for a video in Spanish
python youtube_transcript.py --video_id dQw4w9WgXcQ --output_folder ../../data/transcripts --language es
```

### Output

The script will create two files in the specified output folder:
1. A text file with the transcript in a readable format with timestamps
2. A JSON file with the raw transcript data for potential future use

The filenames include the video ID, language code, and a timestamp to avoid overwriting existing files.

## Other Scripts

- `organize_mds.py`: Organizes markdown files
- `url_downloader.py`: Downloads content from URLs
- `image_transcriber.py`: Transcribes text from images
- `check_model.py`: Checks model availability 