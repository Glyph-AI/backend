from fastapi import HTTPException, status


class Errors:
    login_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    not_authorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    inactive_user = HTTPException(
        status_code=400,
        detail="Inactive User",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sso_user_does_not_exist = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="SSO User does not Exist. Please create a user",
        headers={"WWW-Authenticate": "Bearer"}
    )
    invalid_file_type = HTTPException(
        status_code=400,
        detail="Invalid File Type"
    )
    subscription_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not subscribed",
        headers={"WWW-Authenticate": "Bearer"},
    )
