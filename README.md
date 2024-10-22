´´´
python.exe -m pip install --upgrade pip
pip install requests pony bcrypt pydantic uvicorn fastapi passlib python-jose python-multipart
uvicorn main:app --reload
curl -X POST "http://127.0.0.1:5000/token" -d "username=admin&password=adminpass"
curl -X GET "http://127.0.0.1:5000/logeventos/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcyOTU5MTQxMn0._iVqWkWVp0SQd4r5Ea2zK4QH_2XOr1UpbV3aZiztDNI"
´´´