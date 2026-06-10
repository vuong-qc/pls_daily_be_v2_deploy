from fastapi import HTTPException, status


class FileNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class FileBadRequestException(HTTPException):
    def __init__(self):
        super().__init__(
            detail="Invalid parameter",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
