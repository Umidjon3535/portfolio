import json
import mimetypes
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):
    """Admin'dan yuklangan fayllarni (rasm, CV) Supabase Storage'da saqlaydi.

    Vercel'da disk faqat o'qish uchun, shuning uchun fayllar tashqi xizmatga yoziladi.
    """

    def __init__(self, url=None, key=None, bucket=None):
        self.base = (url or settings.SUPABASE_URL).rstrip('/')
        self.key = key or settings.SUPABASE_SERVICE_KEY
        self.bucket = bucket or settings.SUPABASE_BUCKET

    def _object_url(self, name):
        return f"{self.base}/storage/v1/object/{self.bucket}/{quote(name)}"

    def _request(self, method, url, data=None, headers=None):
        request = Request(url, data=data, method=method, headers={
            'Authorization': f'Bearer {self.key}',
            'apikey': self.key,
            **(headers or {}),
        })
        return urlopen(request, timeout=30)

    def upload(self, name, data, upsert=False):
        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        self._request('POST', self._object_url(name), data=data, headers={
            'Content-Type': content_type,
            'x-upsert': 'true' if upsert else 'false',
        }).close()

    def _save(self, name, content):
        name = name.replace('\\', '/')
        content.seek(0)
        self.upload(name, content.read())
        return name

    def _open(self, name, mode='rb'):
        with self._request('GET', self._object_url(name)) as response:
            return ContentFile(response.read(), name=name)

    def exists(self, name):
        try:
            self._request('HEAD', self._object_url(name)).close()
        except HTTPError:
            return False
        return True

    def delete(self, name):
        try:
            self._request('DELETE', self._object_url(name)).close()
        except HTTPError as error:
            if error.code not in (400, 404):
                raise

    def size(self, name):
        with self._request('HEAD', self._object_url(name)) as response:
            return int(response.headers.get('Content-Length', 0))

    def url(self, name):
        return f"{self.base}/storage/v1/object/public/{self.bucket}/{quote(name)}"

    def create_bucket(self):
        body = json.dumps({'id': self.bucket, 'name': self.bucket, 'public': True}).encode()
        try:
            self._request('POST', f"{self.base}/storage/v1/bucket", data=body,
                          headers={'Content-Type': 'application/json'}).close()
        except HTTPError as error:
            # bucket allaqachon mavjud bo'lsa, xato emas
            if error.code not in (400, 409):
                raise
