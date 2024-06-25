from django.core.exceptions import ValidationError
import os


def allow_only_images_validator(value):
    """
    Validates that the uploaded file is an image with a supported extension.

    This function checks the extension of the uploaded file to ensure it is one of
    the allowed image formats (.png, .jpg, .jpeg). If the file extension is not in 
    the list of valid extensions, it raises a ValidationError.

    Parameters:
    value (File): The uploaded file that needs to be validated.

    Raises:
    ValidationError: If the file extension is not one of the allowed image formats.

    Example:
    ```
    from django.core.exceptions import ValidationError
    from django.core.files.uploadedfile import SimpleUploadedFile

    # Valid file
    file = SimpleUploadedFile("image.jpg", b"file_content")
    allow_only_images_validator(file)  # No exception should be raised

    # Invalid file
    file = SimpleUploadedFile("document.pdf", b"file_content")
    try:
        allow_only_images_validator(file)
    except ValidationError as e:
        print(e)  # 'Unsupported file extension. Allowed extensions: ['.png', '.jpg', '.jpeg']'
    ```
    """
    ext = os.path.splitext(value.name)[1] # cover-image.jpg
    print(ext)
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' +str(valid_extensions))