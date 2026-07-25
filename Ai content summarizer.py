from bs4 import BeautifulSoup
import requests
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi


def get_youtube_transcript(url):
  try:
    # Extract Video ID from URL
    if 'watch?v=' in url:
      video_id = url.split('watch?v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
      video_id = url.split('youtu.be/')[1].split('?')[0]
    else:
      return None

    # Fetch transcript
    transcript_list = YouTubeTranscriptApi.get_transcript(
        video_id, languages=['en', 'hi']
    )
    transcript = ' '.join([item['text'] for item in transcript_list])
    return transcript
  except Exception as e:
    print(f'YouTube Error: {e}')
    return None


def get_web_article(url):
  try:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = ' '.join([p.text for p in paragraphs])
    return article_text
  except Exception as e:
    print(f'Website Error: {e}')
    return None


def summarize_text(text):
  print(
      '\n[INFO] Loading AI model and generating summary, please wait...\n'
  )
  # Load Hugging Face summarization pipeline
  summarizer = pipeline(
      'summarization', model='facebook/bart-large-cnn', device=-1
  )

  # Split text into chunks to handle token limits
  max_chunk = 1000
  text_chunks = [text[i : i + max_chunk] for i in range(0, len(text), max_chunk)]

  summary = ''
  for chunk in text_chunks:
    if len(chunk.strip()) > 50:
      res = summarizer(
          chunk, max_length=130, min_length=30, do_sample=False
      )
      summary += res[0]['summary_text'] + ' '

  return summary


if __name__ == '__main__':
  print('=== AI Content Summarizer ===')
  print('1. YouTube Video')
  print('2. Web Article / Blog')

  choice = input('Select your choice (1 or 2): ').strip()
  url = input('Paste the URL here: ').strip()

  text_to_summarize = ''

  if choice == '1':
    print('[INFO] Extracting YouTube transcript...')
    text_to_summarize = get_youtube_transcript(url)
  elif choice == '2':
    print('[INFO] Reading web article...')
    text_to_summarize = get_web_article(url)
  else:
    print('Invalid choice!')

  if text_to_summarize:
    final_summary = summarize_text(text_to_summarize)
    print('\n' + '=' * 40)
    print('✨ FINAL SUMMARY:')
    print('=' * 40)
    print(final_summary)
  else:
    print('[ERROR] Failed to fetch content. Please provide a valid URL.')

