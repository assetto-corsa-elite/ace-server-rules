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
        archived = [m for m in self.manifests if m['status'] == 'archived']
        self.assertEqual(sum(len(m['posts']) for m in archived), 11)
        self.assertEqual(sum(len(p['attachments']) for m in archived for p in m['posts']), 28)

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
            if manifest['sequence_id'].startswith('test-'):
                continue  # Plain-name TEST rendering is covered in test_manual_test_package.py.
            for post in manifest['posts']:
                if post['kind'] == 'media':
                    continue
                rendered = feed.render(ROOT, post, self.bindings)['content']
                source = feed.checked_bytes(ROOT, post['content']).decode()
                if '{{driver:lilcoughdrop}}' in source:
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


class AnnouncementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FeedRegressionTests.setUpClass.__func__(cls)

    def test_everyone_exactly_on_authorized_messages(self):
        for manifest in self.manifests:
            if manifest['sequence_id'].startswith('test-'):
                continue  # TEST messages never ping; exercise their dedicated renderer separately.
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


class AuditRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FeedRegressionTests.setUpClass.__func__(cls)

    def test_cycles_are_rejected(self):
        manifests = copy.deepcopy(self.manifests)
        manifests[0]['requires_sequences'] = [manifests[1]['sequence_id']]
        manifests[1]['requires_sequences'] = [manifests[0]['sequence_id']]
        with self.assertRaises(feed.FeedError):
            feed.validate_dependencies(manifests)

    def test_announcement_missing_poster_is_rejected(self):
        manifests = copy.deepcopy(self.manifests)
        announcement = next(m for m in manifests if m['phase'] == 'results_announcement')
        announcement['posts'][2]['attachments'].pop()
        with self.assertRaises(feed.FeedError):
            feed.validate_dependencies(manifests)

    def test_wrong_race_day_time_is_rejected(self):
        m = copy.deepcopy(next(m for m in self.manifests if m['phase'] == 'race_day_announcement'))
        m['status'] = 'ready'
        feed.validate_sequence_metadata(m)
        m['scheduled_at'] = '2026-11-21T09:00:00Z'
        with self.assertRaises(feed.FeedError):
            feed.validate_sequence_metadata(m)

    def test_missing_stages_and_completed_sequences(self):
        m = copy.deepcopy(self.sequence)
        m['status'] = 'ready'
        self.assertEqual(feed.due_sequences([m], feed.timestamp('2026-11-29T20:00:00+01:00'), {m['sequence_id']}), [])
        m['posts'].pop()
        with self.assertRaises(feed.FeedError):
            feed.validate_sequence_metadata(m)

    def test_detail_is_allowed_but_code_block_indentation_is_rejected(self):
        text = '# Title\n\n{{emoji:checked}} 📊 **DETAILS**\n• One result.\n• Another result.\n'
        feed.validate_template(text, self.drivers, self.emojis)
        with self.assertRaises(feed.FeedError):
            feed.validate_template(text.replace('• Another', '    • Another'), self.drivers, self.emojis)


class CarouselTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FeedRegressionTests.setUpClass.__func__(cls)
        cls.viewer = next(p for p in cls.sequence['posts'] if p['category'] == 'race_insights')

    def test_navigation_edges_and_one_image_per_screen(self):
        first = feed.render_carousel(self.viewer, 0, 'example-viewer')
        last = feed.render_carousel(self.viewer, 3, 'example-viewer')
        self.assertTrue(first['message']['components'][0]['components'][0]['disabled'])
        self.assertFalse(first['message']['components'][0]['components'][1]['disabled'])
        self.assertTrue(last['message']['components'][0]['components'][1]['disabled'])
        self.assertEqual(first['upload'], self.viewer['attachments'][0])
        self.assertIn('(1/4)', first['message']['embeds'][0]['title'])
        self.assertEqual(len(first['message']['embeds']), 1)
        self.assertEqual(last['message']['allowed_mentions']['parse'], [])

    def test_out_of_range_and_missing_screen_fail(self):
        with self.assertRaises(feed.FeedError):
            feed.render_carousel(self.viewer, 4, 'example-viewer')
        broken = copy.deepcopy(self.viewer)
        broken['presentation']['screens'].pop()
        with self.assertRaises(feed.FeedError):
            feed.validate_presentation(broken)

    def test_protected_posters_stay_direct(self):
        for m in self.manifests:
            for post in m['posts']:
                if post['category'] in ['race_results', 'standings', 'pre_race_briefing', 'pre_race_announcement']:
                    self.assertEqual(post['presentation']['mode'], 'direct')
        wrong = copy.deepcopy(self.post)
        wrong['presentation'] = copy.deepcopy(self.viewer['presentation'])
        with self.assertRaises(feed.FeedError):
            feed.validate_presentation(wrong)

    def test_announcement_keeps_three_messages_and_all_screens(self):
        m = next(m for m in self.manifests if m['phase'] == 'results_announcement')
        self.assertEqual(len(m['posts']), 3)
        self.assertEqual(m['posts'][1]['presentation']['mode'], 'direct')
        self.assertEqual(m['posts'][2]['presentation']['mode'], 'carousel')
        self.assertEqual(len(m['posts'][2]['presentation']['screens']), 10)
        feed.validate_presentation(m['posts'][2])


class StewardingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FeedRegressionTests.setUpClass.__func__(cls)

    def check_gate(self, review, expected_error=False):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            data = json.dumps(review).encode()
            (root / 'review.json').write_bytes(data)
            manifest = copy.deepcopy(self.sequence)
            manifest.update(status='ready', result_snapshot_sha256='a' * 64,
                            stewarding_review={'path': 'review.json', 'sha256': feed.digest(data)})
            if expected_error:
                with self.assertRaises(feed.FeedError):
                    feed.validate_stewarding_gate(root, manifest)
            else:
                feed.validate_stewarding_gate(root, manifest)

    def approved(self):
        return {'league_id': 'league-04', 'round': 4, 'state': 'approved',
                'organizer_supplied': True, 'approval_reference': 'test-organizer-confirmation',
                'numeric_application_state': 'not_required', 'result_snapshot_sha256': 'a' * 64,
                'decisions': []}

    def test_explicit_zero_penalties_and_approval(self):
        review = self.approved()
        self.check_gate(review)
        review['organizer_supplied'] = False
        self.check_gate(review, True)

    def test_numeric_adjustment_requires_verified_acsm(self):
        review = self.approved()
        review['decisions'] = [{'decision_id': 'test-time', 'type': 'time_penalty', 'value': 5}]
        self.check_gate(review, True)
        review['numeric_application_state'] = 'acsm_verified'
        self.check_gate(review)
        review['decisions'][0].update(type='points_deduction', value=10)
        self.check_gate(review)

    def test_changed_results_and_duplicate_decisions_fail(self):
        review = self.approved()
        review['result_snapshot_sha256'] = 'b' * 64
        self.check_gate(review, True)
        review['result_snapshot_sha256'] = 'a' * 64
        decision = {'decision_id': 'same-decision', 'type': 'outstanding_penalty', 'value': 2, 'outstanding_mode': 'award'}
        review['decisions'] = [decision, decision.copy()]
        self.check_gate(review, True)

    def test_stewarding_is_text_only_without_notification(self):
        post = next(p for p in self.sequence['posts'] if p['category'] == 'stewarding_review')
        self.assertEqual(post['attachments'], [])
        self.assertEqual(post['presentation']['mode'], 'direct')
        self.assertFalse(post['mention_everyone'])
        self.assertEqual(post['destination_key'], 'results')


class OutstandingTests(unittest.TestCase):
    def test_large_awards_and_immediate_reset(self):
        for active, award, expected in [(0, 3, 0), (1, 2, 0), (2, 2, 1), (2, 3, 2)]:
            result = feed.advance_outstanding(active, 0, award)
            self.assertEqual(result['active_counter_after'], expected)
            self.assertEqual(result['threshold_events'][0]['ban_required'], 'round_ban')

    def test_second_maximum_keeps_history_and_requires_league_ban(self):
        result = feed.advance_outstanding(1, 1, 2)
        self.assertEqual(result['active_counter_after'], 0)
        self.assertEqual(result['maximum_events_after'], 2)
        self.assertEqual(result['threshold_events'][0]['ban_required'], 'league_ban')
        self.assertEqual(feed.advance_outstanding(0, 0, 2)['threshold_events'], [])

    def test_combined_seconds_points_and_outstanding_are_accepted(self):
        review = StewardingTests.approved(self)
        review['numeric_application_state'] = 'acsm_verified'
        review['decisions'] = [
            {'decision_id': 'case-a-time', 'case_id': 'case-a', 'type': 'time_penalty', 'value': 20},
            {'decision_id': 'case-a-points', 'case_id': 'case-a', 'type': 'points_deduction', 'value': 10},
            {'decision_id': 'case-a-outstanding', 'case_id': 'case-a', 'type': 'outstanding_penalty', 'outstanding_mode': 'award', 'value': 3}]
        FeedRegressionTests.setUpClass()
        self.sequence = FeedRegressionTests.sequence
        StewardingTests.check_gate(self, review)


class StewardWorkflowConfigurationTests(unittest.TestCase):
    def test_deadlines_and_exact_incident_choices(self):
        config = feed.read_json(ROOT / 'config/stewarding.json')
        self.assertEqual(config['report_cutoff']['hour'], 15)
        self.assertEqual(config['finalization_deadline']['hour'], 23)
        self.assertEqual(len(config['incident_types']), 10)
        self.assertIn('Blueflag infraction', config['incident_types'])
        self.assertEqual(config['entrant_source'], 'CM_ENTRANTS')

    def test_reason_modals_and_authorized_roles(self):
        config = feed.read_json(ROOT / 'config/stewarding.json')
        self.assertEqual(config['authorized_role_keys'], ['league-stewards', 'super-admins'])
        self.assertEqual(len(config['sanctions']), 9)
        for sanction in config['sanctions']:
            if sanction['type'] in ['outstanding_penalty', 'round_ban', 'league_ban', 'servers_discord_ban']:
                self.assertTrue(sanction['reason_required'])
        self.assertFalse(config['ready_notification']['mention_everyone'])

    def test_results_are_review_triggered(self):
        config = feed.read_json(ROOT / 'config/publication.json')
        cadence = config['cadences']['post_race']
        self.assertEqual(cadence['trigger'], 'verified_final_stewarding_ready')
        self.assertNotIn('local_time', cadence)
        self.assertEqual(cadence['finalization_deadline'], '23:00')


if __name__ == '__main__':
    unittest.main()
