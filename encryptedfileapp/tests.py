from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from encryptedfileapp.models import EncryptedFile


class FileUploadTestCase(TestCase):
  def setUp(self):
    self.client = Client()

  def test_file_upload(self):
    # Test the file upload functionality
    with open("testfile.txt", "w") as f:
      f.write("Test content for file upload")
    with open("testfile.txt", "rb") as f:
      response = self.client.post(reverse("upload_file"), {"file": f})
    self.assertEqual(response.status_code, 200)

  def test_file_metadata_saved(self):
    # metadata must be saved in the database
    EncryptedFile.objects.create(
        original_file_name="testfile.txt",
        s3_key="test_s3_key",
        encryption_key=b'test_encryption_key',
        iv=b'test_iv'
    )

    file_entry = EncryptedFile.objects.get(original_file_name="testfile.txt")
    self.assertEqual(file_entry.s3_key, "test_s3_key")
