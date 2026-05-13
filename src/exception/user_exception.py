from fastapi import HTTPException, status

class ExceptionUserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f'User not found'
        )
class ExceptionEmailExists(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists'
        )

class ExceptionMasterFoundUserRoleOutScope(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Master only find users with role: handler, interviewer, trainer'
        )
class ExceptionCanNotCreateMaster(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 1 account master in system"
        )
class ExceptionAdminCreateUserOutSCope(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amin only can create users with role: handler, manager, tasker"
        )
class ExceptionMasterUpdateUserOutScope(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master, admin only can update users with role: manager, handler, tasker"
        )
class ExceptionHandlerCreateUserOutScope(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Handler only can create candidate"
        )

class ExceptionUserIsNotValid(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not valid, account is deleted or disable"
        )
class ExceptionUserTokenExpired(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User token is expired"
        )

class ExceptionFindUserRoleOutScope(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User only can find roles: handler, interviewer, trainer"
        )