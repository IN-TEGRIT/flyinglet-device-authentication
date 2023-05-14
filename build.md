1. 라이브러리 설치

sudo pip install pyinstaller

 

2. 라이브러리 설치

pip install python-dotenv
pip install requests



3. 파일 디렉토리로 이동

cd flyinglet-device-authentication



4. flyinglet-device-authentication.py 파일이 있는 디렉토리에서 

pyinstaller --onefile flyinglet-device-authentication.py



5. 실행파일 있는 디렉토리로 이동

cd dist



6. 파일실행

./flyinglet-device-authentication


