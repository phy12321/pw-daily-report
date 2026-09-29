import datetime as dt
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import pipeline as p


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = dt.datetime(2026, 9, 27, tzinfo=p.UTC).timestamp()

    def response(self, more=False, token='next', content='hello', update=None):
        return {'ok': True, 'data': {'messages': [{'message_id': 'm1', 'content': content, 'update_time': update}],
                                    'has_more': more, 'page_token': token}}

    def test_native_pending_preserves_target_but_blocks_old_sender(self):
        p.save(self.root / 'config/private.json', {'publisher': {
            'kind': 'aily_native_delivery', 'status': 'native_delivery_pending',
            'target_verified': True, 'chat_id': 'c1', 'name': 'work partner'}})
        (self.root / 'reports').mkdir()
        (self.root / 'reports/latest.md').write_text('reviewed brief')
        p.prepare_publish(self.root)
        preview = p.read(self.root / 'state/publish-preview.json', {})
        self.assertTrue(preview['target_verified'])
        self.assertEqual(preview['delivery_status'], 'native_delivery_pending')
        self.assertFalse(preview['external_write_performed'])
        def must_not_send(_):
            self.fail('Old sender must not run for native delivery')
        with self.assertRaises(ValueError):
            p.publish_chat(self.root, runner=must_not_send)

    def test_incremental_dedup_and_edit(self):
        seen = {}
        self.assertEqual(len(p.dedup_messages(self.response()['data']['messages'], seen)), 1)
        self.assertEqual(p.dedup_messages(self.response()['data']['messages'], seen), [])
        self.assertEqual(len(p.dedup_messages(self.response(content='edit', update=10)['data']['messages'], seen)), 1)

    def test_partial_preserves_watermark_and_resumes_bounds(self):
        state = {'chats': {'c1': {'watermark': self.now - 100, 'seen': {}}}}
        _, status = p.collect_chat({'id': 'c1'}, state, self.root, self.now,
                                  lambda _: self.response(True), page_limit=1)
        self.assertEqual(status['status'], 'partial')
        self.assertEqual(state['chats']['c1']['watermark'], self.now - 100)
        calls = []
        def done(argv):
            calls.append(argv)
            return self.response()
        _, status = p.collect_chat({'id': 'c1'}, state, self.root, self.now + 100, done)
        self.assertIn('next', calls[0])
        self.assertIn(p.iso(self.now), calls[0])
        self.assertEqual(state['chats']['c1']['watermark'], self.now)
        self.assertNotIn('pending', state['chats']['c1'])

    def test_failure_is_not_empty_success(self):
        p.save(self.root / 'config/private.json', {'chats': [{'id': 'c1'}]})
        def fail(_):
            raise RuntimeError('secret material')
        packet = p.collect(self.root, self.now, runner=fail)
        self.assertEqual(packet['collectors']['chat:c1']['status'], 'error')
        self.assertNotIn('secret', str(packet))
        self.assertNotIn('watermark', p.read(self.root / 'state/cursors.json', {})['chats']['c1'])

    def test_sensitive_lines_removed(self):
        self.assertEqual(p.redact('模型更新\n会议密码: 123456\nsecret=xyz'),
                         '模型更新\n[REDACTED sensitive line]\n[REDACTED sensitive line]')

    def test_cli_error_preserves_scopes_without_credentials(self):
        result = subprocess.CompletedProcess([], 3, '', '{"ok":false,"error":{"type":"authorization","subtype":"missing_scope","missing_scopes":["im:message"],"hint":"secret123"}}')
        with patch('pipeline.subprocess.run', return_value=result):
            with self.assertRaises(p.CliError) as raised:
                p.lark(['im', '+messages-send'])
        self.assertEqual(raised.exception.safe['missing_scopes'], ['im:message'])
        self.assertNotIn('secret123', str(raised.exception.safe))

    def test_feed_filter_and_budget(self):
        raw = b'<rss><channel><item><title>JEPA new</title><link>https://arxiv.org/abs/1</link><pubDate>Sat, 26 Sep 2026 00:00:00 GMT</pubDate></item><item><title>unrelated</title><pubDate>Sat, 26 Sep 2026 00:00:00 GMT</pubDate></item><item><title>JEPA old</title><pubDate>Thu, 01 Jan 2020 00:00:00 GMT</pubDate></item></channel></rss>'
        items, more = p.feed_items(raw, ['JEPA'], self.now - 7*86400, self.now, 10)
        self.assertEqual([i['title'] for i in items], ['JEPA new'])
        self.assertIn('rss_announced_at', items[0])
        self.assertNotIn('published', items[0])
        self.assertFalse(more)
        self.assertTrue(p.feed_items(raw, ['JEPA'], self.now - 7*86400, self.now, 0)[1])

    def test_collect_uses_editable_focus_for_rss_prefilter(self):
        p.save(self.root / 'config/focus.json', {'rss_topic_patterns': ['robot.*manipulat']})
        p.save(self.root / 'config/sources.json', {'feeds': [
            {'id': 'test-feed', 'url': 'https://example.com/rss', 'enabled': True}]})
        raw = (b'<rss><channel>'
               b'<item><title>JEPA representation</title><pubDate>Sat, 26 Sep 2026 00:00:00 GMT</pubDate></item>'
               b'<item><title>Robot manipulation</title><pubDate>Sat, 26 Sep 2026 00:00:00 GMT</pubDate></item>'
               b'</channel></rss>')
        packet = p.collect(self.root, self.now, fetcher=lambda _: raw)
        self.assertEqual([item['title'] for item in packet['items']], ['Robot manipulation'])

    def test_document_revision_dedup(self):
        p.save(self.root / 'config/private.json', {'wiki_urls': ['https://example/wiki/a']})
        runner = lambda _: {'ok': True, 'data': {'document': {'revision_id': 1, 'content': 'model'}}}
        self.assertEqual(len(p.collect(self.root, self.now, runner)['items']), 1)
        self.assertEqual(len(p.collect(self.root, self.now + 1, runner)['items']), 0)
        self.assertEqual(len(p.read(self.root / 'state/evidence-queue.json', {})['items']), 1)

    def test_preview_is_idempotent_and_not_publish(self):
        first = p.prepare_publish(self.root)
        second = p.prepare_publish(self.root)
        self.assertTrue(first['changed'])
        self.assertFalse(second['changed'])
        self.assertFalse(second['published'])
        self.assertFalse(p.read(self.root / 'state/publish-preview.json', {})['external_write_performed'])

    def test_publish_receipt_and_dedup(self):
        p.save(self.root / 'config/private.json', {'publisher': {'kind': 'lark_im_chat', 'status': 'verified', 'chat_id': 'oc_test'}})
        p.render(self.root)
        calls = []
        def send(argv):
            calls.append(argv)
            return {'ok': True, 'data': {'message_id': 'om_test', 'chat_id': 'oc_test'}}
        self.assertTrue(p.publish_chat(self.root, send)['published'])
        self.assertTrue(p.publish_chat(self.root, send)['skipped_duplicate'])
        self.assertEqual(len(calls), 1)
        self.assertLessEqual(len(calls[0][-1]), 50)

    def test_bot_direct_uses_pinned_profile_and_user_not_old_chat(self):
        p.save(self.root / 'config/private.json', {'publisher': {
            'kind': 'lark_bot_dm', 'status': 'verified', 'profile': 'cli_test',
            'identity': 'bot', 'user_id': 'ou_me'}})
        p.render(self.root)
        calls = []
        def send(argv):
            calls.append(argv)
            return {'ok': True, 'identity': 'bot', 'data': {'message_id': 'om_bot', 'chat_id': 'oc_new'}}
        receipt = p.publish_chat(self.root, send)
        self.assertEqual(receipt['chat_id'], 'oc_new')
        self.assertEqual(calls[0][calls[0].index('--as') + 1], 'bot')
        self.assertIn('--markdown', calls[0])
        self.assertIn('cli_test', calls[0])
        self.assertIn('ou_me', calls[0])
        self.assertNotIn('--chat-id', calls[0])
        self.assertTrue(p.publish_chat(self.root, send)['skipped_duplicate'])
        self.assertEqual(len(calls), 1)

    def group_fixture(self):
        day = '2026-09-28'
        content = '# Reviewed group brief\n\nEvidence and caveat.\n'
        p.save(self.root / 'config/private.json', {'group_publisher': {
            'kind': 'lark_bot_group', 'status': 'verified', 'identity': 'bot',
            'profile': 'cli_test', 'chat_id': 'oc_123', 'name': 'PW产研组',
            'start_date': day}})
        (self.root / 'reports').mkdir(exist_ok=True)
        (self.root / f'reports/brief-{day}.md').write_text(content)
        p.save(self.root / f'state/brief-ready-{day}.json', {
            'date': day, 'status': 'reviewed', 'body_path': f'reports/brief-{day}.md',
            'sha256': hashlib.sha256(content.encode()).hexdigest(), 'reviewed_at': '2026-09-28T00:45:00Z'})
        return dt.datetime(2026, 9, 28, 1, tzinfo=p.UTC)

    def test_group_publish_requires_same_day_review_and_0900(self):
        at_nine = self.group_fixture()
        with self.assertRaises(ValueError):
            p.publish_group(self.root, lambda _: self.fail('early send'), at_nine - dt.timedelta(seconds=1))
        ready_path = self.root / 'state/brief-ready-2026-09-28.json'
        ready = p.read(ready_path, {})
        ready['status'] = 'draft'
        p.save(ready_path, ready)
        with self.assertRaises(ValueError):
            p.publish_group(self.root, lambda _: self.fail('unreviewed send'), at_nine)
        ready['status'] = 'reviewed'
        ready['sha256'] = 'wrong'
        p.save(ready_path, ready)
        with self.assertRaises(ValueError):
            p.publish_group(self.root, lambda _: self.fail('hash mismatch send'), at_nine)

    def test_group_publish_pins_bot_chat_and_sends_once(self):
        at_nine = self.group_fixture()
        calls = []
        def send(argv):
            calls.append(argv)
            return {'ok': True, 'identity': 'bot', 'data': {'message_id': 'om_group', 'chat_id': 'oc_123'}}
        self.assertFalse(p.prepare_group(self.root, at_nine)['published'])
        receipt = p.publish_group(self.root, send, at_nine)
        self.assertEqual(receipt['message_id'], 'om_group')
        self.assertEqual(calls[0][calls[0].index('--chat-id') + 1], 'oc_123')
        self.assertEqual(calls[0][calls[0].index('--as') + 1], 'bot')
        self.assertIn('--markdown', calls[0])
        self.assertNotIn('--user-id', calls[0])
        self.assertTrue(p.publish_group(self.root, send, at_nine)['skipped_duplicate'])
        self.assertEqual(len(calls), 1)

    def test_group_receipt_mismatch_does_not_mark_sent(self):
        at_nine = self.group_fixture()
        with self.assertRaises(ValueError):
            p.publish_group(self.root, lambda _: {'ok': True, 'data': {'message_id': 'om_wrong', 'chat_id': 'oc_other'}}, at_nine)
        uncertain = p.read(self.root / 'state/brief-delivery-2026-09-28-group.json', {})
        self.assertEqual(uncertain['status'], 'attempting')
        with self.assertRaises(ValueError):
            p.publish_group(self.root, lambda _: self.fail('must not blindly retry'), at_nine)
        self.assertFalse((self.root / 'state/publish-ledger.json').exists())

    def test_lark_preserves_explicit_bot_identity(self):
        result = subprocess.CompletedProcess([], 0, '{"ok":true}', '')
        with patch('pipeline.subprocess.run', return_value=result) as run:
            p.lark(['im', '+messages-send', '--as', 'bot'])
        argv = run.call_args.args[0]
        self.assertEqual(argv.count('--as'), 1)
        self.assertEqual(argv[argv.index('--as') + 1], 'bot')

    def test_editorial_and_preview_preserve_reviewed_report(self):
        (self.root / 'state').mkdir()
        (self.root / 'state/editorial-brief.md').write_text('Reviewed editorial')
        self.assertIn('Reviewed editorial', p.render(self.root))
        (self.root / 'reports/latest.md').write_text('Final hand edited')
        p.prepare_publish(self.root)
        self.assertEqual(p.read(self.root / 'state/publish-preview.json', {})['profile_content'], 'Final hand edited')

    def test_failed_publish_never_records_success(self):
        p.save(self.root / 'config/private.json', {'publisher': {'kind': 'lark_im_chat', 'status': 'verified', 'chat_id': 'oc_test'}})
        p.render(self.root)
        with self.assertRaises(ValueError):
            p.publish_chat(self.root, lambda _: {'ok': False})
        self.assertFalse((self.root / 'state/publish-ledger.json').exists())


if __name__ == '__main__':
    unittest.main()
