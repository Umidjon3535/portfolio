import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from portfolio.models import AboutMe, Contact, Skill, Work
from portfolio.storage import SupabaseStorage


class IndexTests(TestCase):
    def test_index_renders_without_images(self):
        AboutMe.objects.create(title="About", description="Text")
        Skill.objects.create(title="Python", progress=80)
        Work.objects.create(title="Project")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")

    def test_download_cv_link(self):
        response = self.client.get(reverse("index"))
        self.assertNotContains(response, "Download CV")
        with override_settings(MEDIA_ROOT=tempfile.mkdtemp()):
            AboutMe.objects.create(
                title="About", description="Text",
                cv=SimpleUploadedFile("cv.pdf", b"%PDF-1.4", content_type="application/pdf"),
            )
            response = self.client.get(reverse("index"))
        self.assertContains(response, 'href="/media/cv/cv.pdf"')
        self.assertContains(response, "download>Download CV")

    def test_contact_saves_message(self):
        response = self.client.post(reverse("index"), {
            "name": "Ali", "email": "ali@example.com", "message": "Salom",
        }, follow=True)
        self.assertContains(response, "Xabaringiz uchun rahmat!")
        contact = Contact.objects.get()
        self.assertEqual(contact.message, "Salom")

    @override_settings(EMAIL_HOST_PASSWORD="secret", CONTACT_EMAIL="me@example.com")
    def test_contact_sends_email(self):
        self.client.post(reverse("index"), {
            "name": "Ali", "email": "ali@example.com", "message": "Salom",
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["me@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["ali@example.com"])
        self.assertIn("Salom", mail.outbox[0].body)

    def test_contact_invalid_email_shows_error(self):
        response = self.client.post(reverse("index"), {
            "name": "Ali", "email": "notanemail", "message": "Salom",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alert-danger")
        self.assertFalse(Contact.objects.exists())


class FakeSupabase(BaseHTTPRequestHandler):
    objects = {}

    def log_message(self, *args):
        pass

    def _key(self):
        return self.path.split("/storage/v1/object/", 1)[1]

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if self.headers.get("Authorization") != "Bearer secret":
            self.send_response(403)
        else:
            self.objects[self._key()] = (body, self.headers["Content-Type"])
            self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200 if self._key() in self.objects else 404)
        self.end_headers()

    def do_GET(self):
        body = self.objects[self._key()][0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def do_DELETE(self):
        self.objects.pop(self._key(), None)
        self.send_response(200)
        self.end_headers()


class SupabaseStorageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server = HTTPServer(("127.0.0.1", 0), FakeSupabase)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        super().tearDownClass()

    def test_save_open_url_delete(self):
        base = f"http://127.0.0.1:{self.server.server_port}"
        storage = SupabaseStorage(url=base, key="secret", bucket="media")
        name = storage.save("cv/my cv.pdf", ContentFile(b"%PDF-1.4"))
        self.assertEqual(name, "cv/my cv.pdf")
        self.assertEqual(FakeSupabase.objects["media/cv/my%20cv.pdf"][1], "application/pdf")
        self.assertTrue(storage.exists(name))
        self.assertEqual(storage.open(name).read(), b"%PDF-1.4")
        # bir xil nomli fayl ustiga yozilmaydi, yangi nom beriladi
        self.assertNotEqual(storage.save("cv/my cv.pdf", ContentFile(b"x")), name)
        self.assertEqual(storage.url(name), f"{base}/storage/v1/object/public/media/cv/my%20cv.pdf")
        storage.delete(name)
        self.assertFalse(storage.exists(name))
