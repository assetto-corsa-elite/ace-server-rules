"""Exercise the entire manual TEST package without network access or delivery."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manual_test_renderer', ROOT / 'TEST/tools/render_test.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
feed = renderer.feed


class ManualTestPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, manifests = feed.validate(ROOT)
        cls.manifests = [m for m in manifests if m['sequence_id'].startswith('test-')]
        # Synthetic bindings only for offline checks; never used for real delivery.
        cls.bindings = {
            'emojis': {'checked': {'id': '234567890123456789', 'name': 'd_', 'animated': False}},
            'links': {'results_start': 'https://discord.com/channels/123456789012345678/234567890123456789/345678901234567890'},
        }

    def test_every_message_and_carousel_page_is_marked_and_cannot_ping(self):
        self.assertEqual(len(self.manifests), 5)
        self.assertEqual(sum(len(m['posts']) for m in self.manifests), 13)
        assets = set()
        for manifest in self.manifests:
            self.assertEqual(manifest['status'], 'draft')
            for post in manifest['posts']:
                assets.update(a['path'] for a in post['attachments'])
                pages = len(post['presentation'].get('screens', [None]))
                for page in range(pages):
                    result = renderer.render_test(ROOT, manifest, post, self.bindings, page)
                    message = result['message']
                    self.assertEqual(message['content'].splitlines()[0], renderer.MARKER)
                    self.assertFalse(any(s in message['content'] for s in ('<@', '@everyone', '@here')))
                    self.assertNotIn('{{', message['content'])
                    self.assertEqual(message['allowed_mentions'], renderer.NO_MENTIONS)
                    self.assertLessEqual(feed.utf16_units(message['content']), 2000)
                    self.assertEqual(len(result['uploads']), 1 if post['presentation']['mode'] == 'carousel' else len(post['attachments']))
        self.assertEqual(len(assets), 17)

    def test_sequence_chain_and_results_link_stay_in_test(self):
        previous = None
        for manifest in self.manifests:
            self.assertEqual(manifest['requires_sequences'], [previous] if previous else [])
            previous = manifest['sequence_id']
        announcement = self.manifests[-1]
        self.assertEqual(announcement['link_targets']['results_start'], {
            'sequence_id': 'test-league04-r04-post-race',
            'post_id': 'test-league04-r04-qualifying-report',
        })
        self.assertEqual(feed.due_sequences(self.manifests, feed.timestamp('2026-12-01T12:00:00Z')), [])

    def test_production_renderer_refuses_every_test_post(self):
        for manifest in self.manifests:
            for post in manifest['posts']:
                with self.assertRaisesRegex(feed.FeedError, 'production rendering is forbidden'):
                    feed.render(ROOT, post, self.bindings)

    def test_missing_receipt_blocks_results_announcement(self):
        manifest = self.manifests[-1]
        with self.assertRaisesRegex(feed.FeedError, 'TEST delivery receipts'):
            renderer.render_test(ROOT, manifest, manifest['posts'][0], {'emojis': self.bindings['emojis']})


if __name__ == '__main__':
    unittest.main()
