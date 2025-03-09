#!/usr/bin/env python3
"""
YouTube Transcript Downloader

This script downloads transcripts from YouTube videos and saves them to a specified folder.
Usage:
    python youtube_transcript.py --video_id VIDEO_ID --output_folder OUTPUT_FOLDER [--language LANGUAGE] [--filename FILENAME]

Arguments:
    --video_id: The YouTube video ID (the part after v= in the URL)
    --output_folder: The folder where the transcript will be saved
    --language: Optional. The language code for the transcript (default: en)
    --filename: Optional. Custom name for the output text file (without extension)
"""

import argparse
import os
import sys
from datetime import datetime
try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
except ImportError:
    print("Error: youtube_transcript_api package is not installed.")
    print("Please install it using: pip install youtube-transcript-api")
    sys.exit(1)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Download YouTube video transcripts")
    parser.add_argument("--video_id", required=True, help="YouTube video ID (the part after v= in the URL)")
    parser.add_argument("--output_folder", required=True, help="Folder to save the transcript")
    parser.add_argument("--language", default="en", help="Language code for the transcript (default: en)")
    parser.add_argument("--filename", help="Custom name for the output text file (without extension)")
    return parser.parse_args()

def get_video_transcript(video_id, language="en"):
    """
    Get the transcript for a YouTube video.
    
    Args:
        video_id (str): The YouTube video ID
        language (str): The language code for the transcript
        
    Returns:
        list: A list of transcript segments
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get the transcript in the specified language
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            # If the specified language is not available, get the first available transcript
            transcript = transcript_list.find_transcript([])
            print(f"Warning: Transcript not available in {language}. Using {transcript.language_code} instead.")
        
        return transcript.fetch()
    except TranscriptsDisabled:
        print(f"Error: Transcripts are disabled for video {video_id}")
        return None
    except Exception as e:
        print(f"Error retrieving transcript: {str(e)}")
        return None

def save_transcript(transcript, video_id, output_folder, language, custom_filename=None):
    """
    Save the transcript to a file.
    
    Args:
        transcript (list): The transcript data
        video_id (str): The YouTube video ID
        output_folder (str): The folder to save the transcript
        language (str): The language code of the transcript
        custom_filename (str, optional): Custom name for the output file
        
    Returns:
        str: The path to the saved file
    """
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Create filename with timestamp or use custom filename
    if custom_filename:
        filename = f"{custom_filename}.txt"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{video_id}_{language}_{timestamp}.txt"
    
    filepath = os.path.join(output_folder, filename)
    
    # Save as plain text
    with open(filepath, "w", encoding="utf-8") as f:
        for segment in transcript:
            start_time = format_time(segment['start'])
            f.write(f"[{start_time}] {segment['text']}\n")
    
    return filepath

def format_time(seconds):
    """
    Format time in seconds to MM:SS format.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def main():
    """Main function to download and save YouTube transcript."""
    args = parse_arguments()
    
    print(f"Downloading transcript for video: {args.video_id}")
    transcript = get_video_transcript(args.video_id, args.language)
    
    if transcript:
        filepath = save_transcript(transcript, args.video_id, args.output_folder, args.language, args.filename)
        print(f"Transcript saved to: {filepath}")
    else:
        print("Failed to download transcript.")
        sys.exit(1)

if __name__ == "__main__":
    main() 