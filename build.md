1. 라이브러리 설치
```bash
sudo pip install pyinstaller
```

 

2. 라이브러리 설치

```bash
pip install python-dotenv
pip install requests
```



3. 파일 디렉토리로 이동

```bash
cd flyinglet-device-authentication
```



4. flyinglet-device-authentication.py 파일이 있는 디렉토리에서 

```bash
pyinstaller --onefile flyinglet-device-authentication.py
```



5. 실행파일 있는 디렉토리로 이동

```bash
cd dist
```


6. 파일실행

```bash
sudo chmod +x flyinglet-device-authencation
```



7. 파일실행

```bash
./flyinglet-device-authentication
```


