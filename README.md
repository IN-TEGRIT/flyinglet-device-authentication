### 빌드 환경
* ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=423f791d8a7fd6c80919698fa0f9e214248472f5, for GNU/Linux 2.6.32, stripped


### 설명
* 이 프로젝트는 F-code와 Secret key를 사용하여 로봇의 인증을 가능하게 합니다. 일단 인증되면 로봇 장치 정보는 추가 처리 및 제어를 위해 서버로 안전하게 전송됩니다.
* This project enables authentication of a robot using its F-code and secret key. Once authenticated, the robot device information is securely transmitted to the server for further processing and control.

### 실행방법
아래는 flyinglet-device-authentication 다운로드하고 등록하는 절차입니다.
<br/><br/>
  
1. 터미널을 열고 다음 명령어를 입력하여 git을 설치합니다.
```bash
sudo apt-get install git 
```
<br/><br/>
  
2. 파일을 다운로드 받을 디렉토리로 이동합니다.
```bash
cd /path/to/download/dir
```
<br/><br/>
  
3. git을 사용하여 flyinglet-device-authentication 을 다운로드 합니다.
```bash
git clone https://github.com/IN-TEGRIT/flyinglet-device-authentication.git
```
<br/><br/>
  
4. 다운로드된 flyinglet-device-authentication 디렉토리로 이동합니다.
```bash
cd flyinglet-device-authentication
```
<br/><br/>
  
5. flyinglet-device-authentication 을 실행합니다.
```bash
./flyinglet-device-authentication
```
<br/><br/>
  
6. 실행 후, 등록하려는 f-code와 secret key를 입력합니다.
<br/><br/>
  
등록이 완료되면 flyinglet을 사용할 수 있습니다.

