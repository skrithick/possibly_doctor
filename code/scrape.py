import json
from dotenv import load_dotenv
import os
from firecrawl import FirecrawlApp

load_dotenv()

f = open('urls.two.json', 'r')
urls = json.load(f)
f.close()

app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

for u in urls:
    res = app.scrape(
        url=u['url'],
        formats=['markdown'],
        only_main_content=True
    )

    md = res.markdown

    if '* * *' in md:
        md = md.split('* * *', 1)[-1]

    unwanted = [
        '## References',
        '## Bibliography',
        '## Citations',
        '## Annex',
        '## Appendices',
    ]

    for word in unwanted:
        if word in md:
            md = md.split(word, 1)[0]
    
    md = md.split('\n\n', 1)[1]
    
    filename = f'data/{u['name']}.md'
    f = open(filename, 'w', encoding='utf-8')
    f.write(md)
    f.close()