# YouTube Auto Upload

Automatically upload videos to YouTube using GitHub Actions.

## Features

- 🚀 Automatic video upload to YouTube when videos are pushed to the repository
- 📝 Manual workflow dispatch with custom video details
- 🔒 Secure credential management using GitHub Secrets
- ⚡ Fast and reliable uploads using YouTube Data API v3

## Setup Instructions

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **YouTube Data API v3**
4. Create OAuth 2.0 credentials:
   - Go to "Credentials"  "Create Credentials"  "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the client secrets JSON file

### 2. Generate YouTube Credentials

1. Install required Python packages:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. Run the authentication script to generate credentials:
   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   import json

   SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
   flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
   credentials = flow.run_local_server(port=0)
   
   # Save credentials
   with open('credentials.json', 'w') as f:
       f.write(credentials.to_json())
   ```

### 3. Add Secrets to GitHub

1. Go to your repository  Settings  Secrets and variables  Actions
2. Add the following secrets:
   - `YOUTUBE_CLIENT_SECRETS`: Content of your `client_secrets.json` file
   - `YOUTUBE_CREDENTIALS`: Content of your `credentials.json` file

### 4. Create Upload Script

Create a `scripts/upload_video.py` file in your repository:

```python
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video():
    # Load credentials from environment
    creds_data = json.loads(os.environ['YOUTUBE_CREDENTIALS'])
    credentials = Credentials.from_authorized_user_info(creds_data)
    
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Configure video details
    video_file = 'videos/your_video.mp4'  # Update this path
    
    request_body = {
        'snippet': {
            'title': 'My Video Title',
            'description': 'Video description',
            'tags': ['tag1', 'tag2'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'private'  # or 'public', 'unlisted'
        }
    }
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )
    
    response = request.execute()
    print(f"Video uploaded! Video ID: {response['id']}")

if __name__ == '__main__':
    upload_video()
```

## Usage

### Automatic Upload

1. Add your video files to the `videos/` directory
2. Commit and push to the `main` branch
3. The workflow will automatically trigger and upload the video

### Manual Upload

1. Go to Actions  Upload to YouTube  Run workflow
2. Fill in the required details:
   - Video file path
   - Video title
   - Video description (optional)
   - Video tags (optional)
3. Click "Run workflow"

## Workflow Configuration

The workflow is triggered by:
- Push to `main` branch with changes in `videos/**`
- Manual workflow dispatch

## Important Notes

⚠️ **Security**: Never commit your `client_secrets.json` or `credentials.json` files to the repository. Always use GitHub Secrets.

⚠️ **Quota**: YouTube API has daily quota limits. Check your quota usage in Google Cloud Console.

⚠️ **Video Format**: Ensure your videos are in supported formats (MP4, AVI, MOV, etc.)

## Troubleshooting

- **Authentication Error**: Regenerate your credentials and update GitHub Secrets
- **Quota Exceeded**: Wait for quota reset or request quota increase
- **Upload Failed**: Check video file size and format

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
