# Django Encrypted File Upload

This Django project provides a backend API that allows users to upload files, encrypts them using AES-256 encryption, and stores the encrypted files in Amazon S3. It is designed to demonstrate secure file storage and encryption practices using Django, Cryptography, and AWS S3.

## Extra

I added Decryption functionality to retrieve and decrypt data from the AWS bucket

## Features

- **File Upload**: Upload files through a Django API.
- **AES-256 Encryption**: Securely encrypt files before saving.
- **Amazon S3 Storage**: Store encrypted files in an AWS S3 bucket.
- **File Download**: Download/Decrypt Encrypted files from AWS through Django API.
- **Modular Design**: Follows best practices for clean, maintainable, and secure code.

## Getting Started

Follow the steps below to set up this project locally.

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Django 4.0+
- AWS S3 account and credentials

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/django-encrypted-file-upload.git
   cd django-encrypted-file-upload

   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv env
   source env/bin/activate  # For Windows, use `env\Scripts\activate`

   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt

   ```

4. **Set up AWS S3 credentials**: rename file `settings_sample.py` to `settings.py` Add your AWS credentials in the file
   ```
   AWS_ACCESS_KEY_ID = 'your-access-key-id'
   AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'
   AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
   AWS_S3_REGION_NAME = 'your-region'
   ```
5. **Run migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py makemigrations encryptedfileapp
   python manage.py migrate


   ```

6. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```

### Usage

Upload and Encrypt a File:

- Make a `POST` request to the `/upload/` endpoint, passing the file to be uploaded.
- The file will be encrypted and stored in the specified S3 bucket.
- The response will contain metadata such as the s3_key that you can use to download or further reference the file.

Example:
You can use postman or `curl` as used below

```bash
curl -X POST http://127.0.0.1:8000/upload/ -F 'file=@/path/to/your/file.txt'
```

Download and Decrypt a File:

- Make a `GET` request to the `/download/` endpoint, passing the s3_key of the file to be downloaded
- The file will be downloaded, decrypted, and returned to you.

Example:
You can use Postman or curl to download the file by passing the s3_key as a query parameter:

```bash
curl -X GET "http://127.0.0.1:8000/download/?s3_key=encrypted/file.txt"
```

This will trigger the download of the decrypted file.

### Folder Structure

```
django-encrypted-file-upload/
├── encryptedfileapp/          # Django app folder
│   ├── migrations/            # Django migrations folder
│   ├── __init__.py            # Package marker
│   ├── models.py              # Defines FileUpload model
│   ├── views.py               # Contains the view for file upload, encryption, and S3 storage
│   ├── urls.py                # Routes to the views
│   ├── admin.py               # Registers models in Django admin (optional)
│   ├── apps.py                # App configuration
├── media/                     # Temporary storage for uploaded files
├── django_encrypted_file_upload/   # Project folder
│   ├── __init__.py            # Package marker
│   ├── settings.py            # Django settings, including AWS S3 and encryption configurations
│   ├── urls.py                # Project-level URL routing
│   ├── wsgi.py                # WSGI application
├── manage.py                  # Django management script
├── requirements.txt           # Python package dependencies
└── README.md                  # Project documentation

```

### License
