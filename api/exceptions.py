from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"},
)

user_exists_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="User already exists"
)

user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)

location_exists_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Location already exists"
)

location_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
)
