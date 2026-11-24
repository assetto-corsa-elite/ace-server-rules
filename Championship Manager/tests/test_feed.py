import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cm_feed', ROOT / 'tools/feed.py')
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)


class FeedRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog, cls.manifests = feed.validate(ROOT)
        cls.sequence = next(m for m in cls.manifests if m['phase'] == 'post_race')
        cls.post = cls.sequence['posts'][1]
        cls.drivers = feed.read_json(ROOT / 'config/identities.json')['drivers']
        cls.emojis = feed.read_json(ROOT / 'config/emojis.json')['emojis']
        cls.bindings = {'drivers': {key: str(123456789012345670 + i) for i, key in enumerate(cls.drivers)},
                        'emojis': {'checked': {'id': '234567890123456789', 'name': 'd_', 'animated': False}}, 'links': {'results_start': 'https://discord.com/channels/123456789012345678/234567890123456789/345678901234567890'}}

    def test_catalog_and_all_assets(self):
        self.assertEqual(sum(len(m['posts']) for m in self.manifests), 10)
        self.assertEqual(sum(len(p['attachments']) for m in self.manifests for p in m['posts']), 28)

    def test_historical_import_cannot_repost_on_first_connection(self):
        self.assertEqual(feed.due_sequences(self.manifests, feed.timestamp('2026-11-29T23:00:00+01:00')), [])

    def test_ready_sequence_runs_at_exact_due_time_in_utc(self):
        m = copy.deepcopy(self.sequence)
        m['status'] = 'ready'
        self.assertEqual(feed.due_sequences([m], feed.timestamp('2026-11-22T18:59:59Z')), [])
        self.assertEqual(feed.due_sequences([m], feed.timestamp('2026-11-22T19:00:00Z'))[0]['sequence_id'], m['sequence_id'])

    def test_expiry_and_review_gate(self):
        m = copy.deepcopy(self.sequence)
        m.update(status='ready', expires_at='2026-11-23T20:00:00+01:00')
        self.assertEqual(feed.due_sequences([m], feed.timestamp(m['expires_at'])), [])
        m['race_review_complete'] = False
        with self.assertRaises(feed.FeedError):
            feed.due_sequences([m], feed.timestamp('2026-11-22T20:00:00+01:00'))

    def test_prerequisites_wait_for_completed_delivery(self):
        m = copy.deepcopy(self.sequence)
        m.update(status='ready', requires_sequences=['previous-sequence'])
        now = feed.timestamp('2026-11-23T20:00:00+01:00')
        self.assertEqual(feed.due_sequences([m], now), [])
        self.assertEqual(len(feed.due_sequences([m], now, {'previous-sequence'})), 1)

    def test_checked_emoji_is_native_and_underscores_are_preserved(self):
        payload = feed.render(ROOT, self.post, self.bindings)
        self.assertIn('<:d_:234567890123456789>', payload['content'])
        self.assertNotIn('{{', payload['content'])
        self.assertNotIn(':d_:', payload['content'].replace('<:d_:234567890123456789>', ''))
        self.assertEqual(payload['allowed_mentions']['parse'], [])

    def test_driver_id_stays_identical_across_every_post(self):
        expected = '<@' + self.bindings['drivers']['lilcoughdrop'] + '>'
        for manifest in self.manifests:
            for post in manifest['posts']:
                if post['kind'] == 'media':
                    continue
                rendered = feed.render(ROOT, post, self.bindings)['content']
                self.assertIn(expected, rendered)
                self.assertLessEqual(feed.utf16_units(rendered), 2000)

    def test_missing_mapping_and_wrong_emoji_fail_clearly(self):
        bad = copy.deepcopy(self.bindings)
        bad['drivers'].pop('eugene')
        with self.assertRaises(feed.FeedError):
            feed.render(ROOT, self.post, bad)
        bad = copy.deepcopy(self.bindings)
        bad['emojis']['checked']['name'] = 'd'
        with self.assertRaises(feed.FeedError):
            feed.render(ROOT, self.post, bad)

    def test_text_artifacts_are_rejected(self):
        body = '# Title\n\n{{emoji:checked}} 🏁 **RESULT**\nMuchacho\\_AC finishes P4.\n'
        feed.validate_template(body, self.drivers, self.emojis)
        for wrong in ['Muchacho_AC', 'â€”', '<:d:234567890123456789>', '@new_guess']:
            with self.subTest(wrong=wrong), self.assertRaises(feed.FeedError):
                feed.validate_template(body.replace('Muchacho\\_AC', wrong), self.drivers, self.emojis)

    def test_utf16_limit_counts_non_bmp_characters(self):
        self.assertEqual(feed.utf16_units('🏁'), 2)
        with self.assertRaises(feed.FeedError):
            feed.validate_template('# T\n\n{{emoji:checked}} 🏁 **A**\n' + '🏁' * 1000, self.drivers, self.emojis)

    def test_revision_has_no_effect_on_delivery_identity(self):
        key = feed.delivery_key('guild', 'channel', self.sequence['sequence_id'], self.post['post_id'])
        self.assertEqual(feed.message_nonce(key), feed.message_nonce(key))
        self.assertLessEqual(len(feed.message_nonce(key)), 25)
        self.assertNotEqual(key, feed.delivery_key('guild', 'other-channel', self.sequence['sequence_id'], self.post['post_id']))

    def test_corrupt_hash_and_path_escape_fail(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / 'x').write_bytes(b'actual')
            with self.assertRaises(feed.FeedError):
                feed.checked_bytes(root, {'path': 'x', 'sha256': '0' * 64})
            with self.assertRaises(feed.FeedError):
                feed.asset_path(root, '../outside')
            with self.assertRaises(feed.FeedError):
                feed.asset_path(root, '/etc/passwd')

    def test_all_template_sections_are_structured(self):
        for manifest in self.manifests:
            orders = [post['order'] for post in manifest['posts']]
            self.assertEqual(orders, list(range(1, len(orders) + 1)))
            for post in manifest['posts']:
                if post['kind'] == 'media':
                    continue
                body = feed.checked_bytes(ROOT, post['content']).decode()
                self.assertFalse(body.startswith('\ufeff'))
                feed.validate_template(body, self.drivers, self.emojis)


class AnnouncementTests(FeedRegressionTests):
    def test_everyone_exactly_on_authorized_messages(self):
        for manifest in self.manifests:
            for post in manifest['posts']:
                payload = feed.render(ROOT, post, self.bindings)
                self.assertEqual(payload['content'].startswith('@everyone'), post['mention_everyone'])
                self.assertEqual('everyone' in payload['allowed_mentions']['parse'], post['mention_everyone'])

    def test_results_link_resolves_from_ledger(self):
        announcement = next(m for m in self.manifests if m['phase'] == 'results_announcement')
        payload = feed.render(ROOT, announcement['posts'][0], self.bindings)
        self.assertIn(self.bindings['links']['results_start'], payload['content'])
        bad = copy.deepcopy(self.bindings)
        bad.pop('links')
        with self.assertRaises(feed.FeedError):
            feed.render(ROOT, announcement['posts'][0], bad)

    def test_media_posts_are_image_only_and_cover_every_poster(self):
        announcement = next(m for m in self.manifests if m['phase'] == 'results_announcement')
        self.assertEqual([len(p['attachments']) for p in announcement['posts']], [0, 2, 10])
        images = [a['path'] for p in announcement['posts'] for a in p['attachments']]
        source = [a['path'] for p in self.sequence['posts'] for a in p['attachments']]
        self.assertEqual(sorted(images), sorted(source))
        self.assertEqual(len(images), len(set(images)))
        for post in announcement['posts'][1:]:
            self.assertEqual(feed.render(ROOT, post, self.bindings)['content'], '')

    def test_forbidden_ping_and_wrong_channel_fail(self):
        wrong = copy.deepcopy(self.post)
        wrong['mention_everyone'] = True
        with self.assertRaises(feed.FeedError):
            feed.render(ROOT, wrong, self.bindings)
        wrong = copy.deepcopy(self.post)
        wrong['destination_key'] = 'announcements'
        with self.assertRaises(feed.FeedError):
            feed.render(ROOT, wrong, self.bindings)


if __name__ == '__main__':
    unittest.main()
