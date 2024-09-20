from django.db import models

class EncryptedFile(models.Model):
    original_file_name = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    encryption_key = models.BinaryField()
    iv = models.BinaryField()              

    def __str__(self):
        return self.original_file_name
