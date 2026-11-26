#!/usr/bin/env python3
"""Read-only manual TEST payload renderer. Never sends, schedules or writes sanctions."""
from pathlib import Path
import argparse
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('cm_feed_test_reference', ROOT / 'tools/feed.py')
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)
MARKER = 'TEST AUTOMATIC POST RESULTS'
NO_MENTIONS = {'parse': [], 'users': [], 'roles': [], 'replied_user': False}


def render_test(root, manifest, post, bindings, page=0):
    """Call only after validating the pinned catalog; this never authorizes a send."""
    if not manifest['sequence_id'].startswith('test-') or not post['post_id'].startswith('test-'):
        raise feed.FeedError('Manual TEST renderer requires TEST sequence and post IDs')
    if post not in manifest['posts']:
        raise feed.FeedError('Post is outside selected TEST sequence')
    if manifest['status'] != 'draft':
        raise feed.FeedError('This manual-only fixture must remain draft')
    feed.validate_post_policy(post)
    text = ''
    if post['kind'] == 'text':
        text = feed.checked_bytes(root, post['content']).decode('utf-8')
        registry = feed.read_json(root / 'config/identities.json')['drivers']
        emojis = feed.read_json(root / 'config/emojis.json')['emojis']
        feed.validate_template(text, registry, emojis, post['mention_everyone'])
        def replace(match):
            kind, key = match.groups()
            if kind == 'driver':
                # Plain display names only; never look up or emit a driver's snowflake.
                return registry[key]['display_name'].replace('_', '\\_')
            if kind == 'link':
                value = bindings.get('links', {}).get(key)
                if not isinstance(value, str) or not re.fullmatch(r'https://discord\.com/channels/[0-9]{17,20}/[0-9]{17,20}/[0-9]{17,20}', value):
                    raise feed.FeedError('Resolve TEST results_start from TEST delivery receipts')
                return value
            value = bindings.get('emojis', {}).get(key, {})
            ident, name = value.get('id'), value.get('name')
            if not isinstance(ident, str) or not feed.SNOWFLAKE.fullmatch(ident) or name != emojis[key]['name']:
                raise feed.FeedError('Bind verified checked emoji in CM before TEST rendering')
            return '<' + ('a' if value.get('animated') else '') + ':' + name + ':' + ident + '>'
        text = feed.TOKEN.sub(replace, text)
    payload = {'content': MARKER + ('\n' + text if text else ''), 'allowed_mentions': dict(NO_MENTIONS)}
    if any(token in payload['content'] for token in ['@everyone', '@here', '<@']):
        raise feed.FeedError('TEST output must not contain a player, role or mass mention')
    if feed.utf16_units(payload['content']) > 2000:
        raise feed.FeedError('TEST header makes message exceed Discord content limit')
    uploads = post['attachments']
    if post['presentation']['mode'] == 'carousel':
        fragment = feed.render_carousel(post, page, 'manual-test-preview')
        payload.update(fragment['message'])
        uploads = [fragment['upload']]
        # The source's prefix remains in normal message content on every page.
    return {'message': payload, 'uploads': uploads}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--sequence-id', required=True)
    parser.add_argument('--post-id', required=True)
    parser.add_argument('--bindings', type=Path, required=True)
    parser.add_argument('--page', type=int, default=0)
    args = parser.parse_args()
    _, sequences = feed.validate(args.root)
    seq = next(s for s in sequences if s['sequence_id'] == args.sequence_id)
    post = next(p for p in seq['posts'] if p['post_id'] == args.post_id)
    print(json.dumps(render_test(args.root, seq, post, feed.read_json(args.bindings), args.page), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
