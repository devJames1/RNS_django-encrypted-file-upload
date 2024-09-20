import boto3
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os, io, base64, logging
from .models import EncryptedFile
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

# Encryption Function 
def encrypt_file(file_data):
    try:
        key = os.urandom(32)  # AES-256 key (32 bytes)
        iv = os.urandom(16)   # Initialization vector (16 bytes)

        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(file_data) + encryptor.finalize()

        return key, iv, encrypted_data
    except Exception as e:
        logger.error(f"Error during encryption: {e}")
        raise ValueError("Encryption failed")
    

# Decryption Function 
def decrypt_file(key, iv, encrypted_data):
    try:
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data
    except Exception as e:
        logger.error(f"Error during decryption: {e}")
        raise ValueError("Decryption failed")

def get_encryption_parameters(s3_key):
    try:
        encrypted_file = EncryptedFile.objects.get(s3_key=s3_key)
        return encrypted_file.encryption_key, encrypted_file.iv
    except EncryptedFile.DoesNotExist:
        logger.error(f"No encryption parameters found for s3_key: {s3_key}")
        raise ValueError("Encryption parameters not found")



# File upload API
@api_view(["POST"])
def upload_file(request):
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    try:
        file = request.FILES["file"]
        file_name = file.name
        file_data = file.read()

        # Encrypt the file
        try:
            key, iv, encrypted_data = encrypt_file(file_data)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=500)

        # Upload encrypted file to S3
        s3 = boto3.client("s3",
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Generate a unique s3 key
        s3_key = f"encrypted/{file_name}"

        try:
            s3.upload_fileobj(io.BytesIO(encrypted_data), settings.AWS_STORAGE_BUCKET_NAME, s3_key)
        except (BotoCoreError, ClientError) as s3_error:
            logger.error(f"S3 upload error: {s3_error}")
            return JsonResponse({"error": "Failed to upload to S3"}, status=500)

        # Save metadata to database
        try:
            EncryptedFile.objects.create(
                  original_file_name=file_name,
                  s3_key=s3_key,
                  encryption_key=key,
                  iv=iv
                  )
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            return JsonResponse({"error": "Failed to save metadata"}, status=500)

        return JsonResponse({"message": "File uploaded and encrypted successfully", "s3_key": s3_key})

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)


# File download and decryption API
@api_view(["GET"])
def download_file(request):
    s3_key = request.GET.get('s3_key')
    
    if not s3_key:
        return JsonResponse({"error": "S3 key is required"}, status=400)
    
    # Fetch encryption parameters (key and IV) from the database or storage
    key, iv = get_encryption_parameters(s3_key)
    
    if not key or not iv:
        return JsonResponse({"error": "Encryption parameters not found"}, status=404)

    # Download the encrypted file from S3
    s3 = boto3.client("s3",
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        encrypted_file = io.BytesIO()
        s3.download_fileobj(settings.AWS_STORAGE_BUCKET_NAME, s3_key, encrypted_file)
        encrypted_file.seek(0)  # Reset the file pointer after download
        encrypted_data = encrypted_file.read()
    except Exception as e:
        logger.error(f"Failed to download from S3: {e}")
        return JsonResponse({"error": "Failed to download file from S3"}, status=500)

    # Decrypt the file
    try:
        decrypted_data = decrypt_file(key, iv, encrypted_data)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=500)

    # Return the decrypted file as a response (as a downloadable file)
    response = HttpResponse(decrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{s3_key.split("/")[-1]}"'
    
    return response