"""Explicit, bounded Search1API calls; no retries or automatic top-ups."""
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import pipeline

ROOT = Path(__file__).resolve().parent

def call(endpoint, payload=None):
    key = os.environ.get('SEARCH1API_KEY')
    if not key:
        key = pipeline.read(ROOT / 'config/secrets.json', {}).get('search1api_key')
    if not key:
        raise RuntimeError('search1api_key_not_configured')
    if endpoint not in ('usage', 'crawl', 'search'):
        raise ValueError('unsupported_endpoint')
    request = urllib.request.Request('https://api.search1api.com/' + endpoint,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'Authorization': 'Bearer ' + key, 'User-Agent': 'attention-brief/0.1',
                 'Content-Type': 'application/json', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('search1api_http_' + str(error.code)) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError('search1api_network_error') from None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['usage', 'crawl', 'search'])
    parser.add_argument('--url')
    parser.add_argument('--query')
    args = parser.parse_args()
    if args.action == 'usage':
        print(json.dumps({'credits': call('usage').get('usage')}))
        return
    if args.action == 'crawl':
        if not args.url or not args.url.startswith('https://mp.weixin.qq.com/'):
            parser.error('crawl requires a public WeChat HTTPS article URL')
        payload = {'url': args.url}
    else:
        if not args.query:
            parser.error('search requires --query')
        payload = {'query': args.query, 'search_service': 'wechat', 'max_results': 10, 'crawl_results': 0}
    before = call('usage').get('usage')
    if not isinstance(before, (int, float)) or before < 1:
        raise RuntimeError('insufficient_or_unknown_credits')
    result = call(args.action, payload)
    target = ROOT / 'state/search1api' / (pipeline.digest([args.action, payload]) + '.json')
    pipeline.save(target, result)
    print(json.dumps({'saved': str(target), 'credits_before': before,
                      'credits_after': call('usage').get('usage')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
