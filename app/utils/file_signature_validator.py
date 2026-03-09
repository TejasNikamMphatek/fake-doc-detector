import magic

ALLOWED_SIGNATURES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}


def validate_file_signature(file_bytes: bytes):

    mime = magic.from_buffer(file_bytes, mime=True)

    if mime not in ALLOWED_SIGNATURES:
        return False, mime

    return True, mime