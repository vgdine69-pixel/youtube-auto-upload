#!/usr/bin/env python3
"""
YouTube Video Upload Script
Uploads videos to YouTube using the YouTube Data API v3
"""

import os
import sys
import json
import argparse
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


def load_credentials():
    """Load YouTube API credentials from environment variable"""
    try:
        creds_json = os.environ.get('YOUTUBE_CREDENTIALS')
        if not creds_json:
            raise ValueError("YOUTUBE_CREDENTIALS environment variable not set")
        
        creds_data = json.loads(creds_json)
        credentials = Credentials.from_authorized_user_info(creds_data)
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {e}")
        sys.exit(1)


def upload_video(youtube, video_file, title, description, category_id="22", privacy_status="public", tags=None):
    """
    Upload a video to YouTube
    
    Args:
        youtube: YouTube API service object
        video_file: Path to the video file
        title: Video title
        description: Video description
        category_id: YouTube category ID (default: 22 = People & Blogs)
        privacy_status: Video privacy status (public, private, unlisted)
        tags: List of tags for the video
    
    Returns:
        Video ID if successful, None otherwise
    """
    if tags is None:
        tags = []
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }
    
    try:
        # Create MediaFileUpload object
        media = MediaFileUpload(
            video_file,
            chunksize=1024*1024,  # 1MB chunks
            resumable=True
        )
        
        # Call the API's videos.insert method
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        print(f"Uploading video: {title}")
        print(f"File: {video_file}")
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"Upload progress: {progress}%")
        
        video_id = response['id']
        print(f"\n✅ Video uploaded successfully!")
        print(f"Video ID: {video_id}")
        print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
        
        return video_id
        
    except HttpError as e:
        print(f"❌ HTTP Error occurred: {e}")
        return None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Upload videos to YouTube')
    parser.add_argument('video_file', help='Path to the video file to upload')
    parser.add_argument('--title', required=True, help='Video title')
    parser.add_argument('--description', default='', help='Video description')
    parser.add_argument('--category', default='22', help='YouTube category ID (default: 22 = People & Blogs)')
    parser.add_argument('--privacy', default='public', choices=['public', 'private', 'unlisted'], 
                        help='Privacy status (default: public)')
    parser.add_argument('--tags', nargs='*', default=[], help='Video tags (space-separated)')
    
    args = parser.parse_args()
    
    # Check if video file exists
    if not os.path.exists(args.video_file):
        print(f"❌ Error: Video file not found: {args.video_file}")
        sys.exit(1)
    
    # Load credentials
    print("Loading YouTube API credentials...")
    credentials = load_credentials()
    
    # Build YouTube API service
    print("Connecting to YouTube API...")
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Upload video
    video_id = upload_video(
        youtube=youtube,
        video_file=args.video_file,
        title=args.title,
        description=args.description,
        category_id=args.category,
        privacy_status=args.privacy,
        tags=args.tags
    )
    
    if video_id:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
