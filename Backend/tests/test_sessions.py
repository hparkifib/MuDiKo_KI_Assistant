import io
import os
import json
import unittest

# Ensure we can import the Flask app
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'app'
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402


class SessionFlowTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.uploads_base = os.path.join(app.root_path, 'Uploads')
        os.makedirs(self.uploads_base, exist_ok=True)

    def _start_session(self):
        resp = self.client.post('/api/session/start')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get('success'))
        sid = data.get('sessionId')
        self.assertIsNotNone(sid)
        return sid

    def _end_session(self, sid):
        resp = self.client.post('/api/session/end', json={'sessionId': sid})
        # 200 even if already deleted
        self.assertEqual(resp.status_code, 200)

    def test_session_start_end_creates_and_deletes_dir(self):
        sid = self._start_session()
        session_dir = os.path.join(self.uploads_base, sid)
        self.assertTrue(os.path.isdir(session_dir))

        self._end_session(sid)
        self.assertFalse(os.path.exists(session_dir))

    def test_upload_and_serve_and_cleanup(self):
        sid = self._start_session()
        session_dir = os.path.join(self.uploads_base, sid)

        data = {
            'referenz': (io.BytesIO(b'MP3DATA'), 'ref.mp3'),
            'schueler': (io.BytesIO(b'MP3DATA2'), 'sch.mp3'),
        }
        resp = self.client.post('/api/upload-audio', data=data, content_type='multipart/form-data', headers={'X-Session-ID': sid})
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertTrue(body.get('success'))
        self.assertIn('file_map', body)
        self.assertEqual(body['file_map']['schueler'], 'schueler.mp3')
        self.assertEqual(body['file_map']['referenz'], 'referenz.mp3')

        # Files should exist
        self.assertTrue(os.path.isfile(os.path.join(session_dir, 'schueler.mp3')))
        self.assertTrue(os.path.isfile(os.path.join(session_dir, 'referenz.mp3')))

        # Serve audio (schueler)
        resp = self.client.get(f"/api/audio/schueler.mp3?sessionId={sid}")
        self.assertEqual(resp.status_code, 200)

        # Cleanup session
        self._end_session(sid)
        self.assertFalse(os.path.exists(session_dir))

    def test_generate_feedback_requires_files(self):
        sid = self._start_session()
        payload = {
            'language': 'deutsch',
            'customLanguage': '',
            'referenzInstrument': 'keine Angabe',
            'schuelerInstrument': 'keine Angabe',
            'personalMessage': '',
            'prompt_type': 'contextual',
            'use_simple_language': False,
            'sessionId': sid,
        }
        resp = self.client.post('/api/generate-feedback', data=json.dumps(payload), content_type='application/json', headers={'X-Session-ID': sid})
        # Should fail because files are missing
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertIn('error', data)

        # Cleanup
        self._end_session(sid)


if __name__ == '__main__':
    unittest.main()
