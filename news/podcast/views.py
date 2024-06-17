# podcast/views.py
import feedparser
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Article
from .serializers import ArticleSerializer
import boto3
import json

RSS_FEEDS = {
    "music": [
        {"url": "https://www.npr.org/rss/rss.php?id=1039", "title": "NPR Classical", "description": "Classical music news", "usability": "usable with attribution"},
        {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "title": "BBC News - World", "description": "World news from BBC", "usability": "usable with attribution"},
        {"url": "http://rss.cnn.com/rss/edition.rss", "title": "CNN - Top Stories", "description": "Top stories from CNN", "usability": "usable with attribution"},
        {"url": "https://www.npr.org/rss/rss.php?id=1001", "title": "NPR - News", "description": "News from NPR", "usability": "usable with attribution"},
        {"url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "title": "The New York Times - World News", "description": "World news from The New York Times", "usability": "usable with attribution"},
        # {"url": "http://feeds.reuters.com/reuters/topNews", "title": "Reuters - Top News", "description": "Top news from Reuters", "usability": "usable with attribution"},
        {"url": "http://feeds.feedburner.com/TechCrunch/", "title": "TechCrunch", "description": "Latest technology news from TechCrunch", "usability": "usable with attribution"},
        # {"url": "https://www.wired.com/feed/category/tech/latest/rss", "title": "Wired - Technology", "description": "Latest technology news from Wired", "usability": "usable with attribution"},
        {"url": "https://www.theguardian.com/world/rss", "title": "The Guardian - World News", "description": "World news from The Guardian", "usability": "usable with attribution"},
        {"url": "https://www.espn.com/espn/rss/news", "title": "ESPN - Top Headlines", "description": "Top sports news from ESPN", "usability": "usable with attribution"},
        {"url": "https://news.ycombinator.com/rss", "title": "Hacker News", "description": "Latest tech news from Hacker News", "usability": "usable with attribution"}
    ],
    # Add more categories and feeds as needed
}

@api_view(['GET'])
def search_feeds(request):
    category = request.GET.get('category')
    
    if category is None:
        return JsonResponse({"error": "Category is missing."}, status=400)

    feeds = RSS_FEEDS.get(category.lower(), [])
    return JsonResponse({"feeds": feeds})

@api_view(['GET'])
def get_articles(request):
    feed_url = request.GET.get('feed_url')

    if feed_url is None:
        return JsonResponse({"error": "Feed URL is missing."}, status=400)

    # Debugging statement
    print(f"Feed URL: {feed_url}")

    feed = feedparser.parse(feed_url)

    if feed.bozo:
        return JsonResponse({"error": "Failed to parse feed."}, status=400)

    articles = []
    for entry in feed.entries:
        article = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "published": entry.get("published", "")
        }
        articles.append(article)

    return JsonResponse({"articles": articles})

    

@api_view(['POST'])
def transcribe_to_audio(request):
    data = json.loads(request.body)
    article = data['article']
    
    # Extract source information
    source_title = article.get('source', {}).get('title', 'Unknown Source')
    source_url = article.get('source', {}).get('url', '')

    # Text to transcribe
    text_to_transcribe = f"Article from {source_title}. {article['description']}. For more details, visit {source_url}."

    # Transcribe article text to audio using AWS Polly
    polly_client = boto3.Session().client('polly')
    response = polly_client.synthesize_speech(
        VoiceId='Joanna',
        OutputFormat='mp3',
        Text=text_to_transcribe
    )
    audio_stream = response['AudioStream'].read()

    # Save article and audio to the database
    article_instance = Article.objects.create(
        title=article['title'],
        link=article['link'],
        description=article['description'],
        transcript=text_to_transcribe,
        audio=audio_stream
    )
    serializer = ArticleSerializer(article_instance)
    return JsonResponse({"article": serializer.data})
