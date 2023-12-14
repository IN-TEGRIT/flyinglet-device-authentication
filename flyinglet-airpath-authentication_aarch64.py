import curses
import curses.ascii
import uuid
import requests
import os
import argparse
import time
import datetime
import platform
import socket
from dotenv import set_key
import logging


# 로깅 레벨 설정 (예: INFO)
logging.basicConfig(level=logging.INFO)

# 로그 파일 경로 설정
log_file_path = './flyinglet-device-authentication-v2.0.0.log'

# 로그 핸들러 생성 (파일에 로그를 기록)
file_handler = logging.FileHandler(log_file_path)

# 로그 포매터 설정 (원하는 형식으로 로그를 출력)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 로거 생성 및 핸들러 추가
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

class InstallIntegrit:
    def __init__(self):
        self.mac_address = None
        self.getnode = None
        self.machine = None
        self.node = None
        self.platform = None
        self.processor = None
        self.release = None
        self.system = None
        self.version = None
        self.uname = None
        self.authentication_timestamp = None
        self.env_path = os.path.expanduser('~/.flyinglet/.env')
        self.env_vars = {}
        self.airpath_path = os.path.expanduser('/persist/data/.sysinfo')
        self.env_vars = {}

        if os.path.exists(self.env_path):
            # .env 파일이 존재할 경우, 해당 파일을 로드
            logger.info("/.env 파일 있음...")
            with open(self.env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and len(line.split('=', 1)) == 2:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        else:
            # .env 파일이 존재하지 않을 경우, 생성
            logger.info("/.env 파일 없음...")
            os.makedirs(os.path.dirname(self.env_path), exist_ok=True)
            with open(self.env_path, 'w') as f:
                f.write('# Add your environment variables here\n')
            print(f'{self.env_path} has been created.')
            logger.info("/.env 파일 생성함")


        # try:
        # airpath_info.json JSON 파일 읽기
        with open(self.airpath_path, 'r', encoding='UTF-8') as file:
            # 파일 내용
            file_contents = file.read()
            # 파일 내용을 문자열로 디코딩
            file_contents_str = file_contents
            # 줄 바꿈 문자로 분할한 후 키-값 쌍 추출 및 딕셔너리로 저장
            data = {}
            lines = file_contents_str.split('\n')   # 윈도우: \\n  우분투: \n
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)  # 첫 번째 ':'만 기준으로 분리
                    data[key.strip()] = value.strip()

            # 딕셔너리 출력
            print(data)

        # except:
        #     data = {}

        # 변환된 데이터 사용
        self.sn = data.get('MB', None)
        self.som_sn = data.get('SOM', None)
        self.name = data.get('MODEL', None)
        self.airpath_version = data.get('HW', None)
        self.sw = data.get('SW', None)

    def check_network_connection(self, timeout=3, retry_count=10):
        # 연결 상태 확인할 호스트와 포트
        logger.info("네트워크 상태 점검")
        host = "www.google.com"
        port = 80
        for i in range(retry_count):
            try:
                logger.info("네트워크 접속시도...")
                socket.setdefaulttimeout(timeout)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                return True
            except socket.error as ex:
                time.sleep(1)  # 1초 대기 후 재시도
                logger.info(f"네트워크 접속 재시도...{i+1}")

        return False


    def Boot_routine(self):
        # Get sn - fcode
        sn_registry = self.get_sn_registry()
        if sn_registry is False or self.check_data(self.sn) is False:
            return print(False)
        else:
            fcode = sn_registry['fCode']
            if (os.environ.get('FCODE','').strip('\"\'') != fcode or
                    os.environ.get('AUTHENTICATION_TIMESTAMP','').strip('\"\'') != fcode or
                    sn_registry['mac_address'] != self.mac_address):
                self.get_mac_address()
                # Send to MongoDB
                now = datetime.datetime.now()
                unix_time = int(time.mktime(now.timetuple()))
                self.authentication_timestamp = unix_time

                # F-code 환경변수에 저장
                set_key(self.env_path, 'AUTHENTICATION_TIMESTAMP', str(self.authentication_timestamp))
                set_key(self.env_path, 'FCODE', str(fcode))
                self.send_macaddress(fcode)
            else:
                pass


    def argpaser(self):
        if self.check_network_connection(retry_count=10):
            # try:
            self.Boot_routine()
            # except Exception as e:
            #     print("An error occurred:", e)
        else:
            exit()

    def get_mac_address(self):
        # Get MAC address
        self.mac_address = ':'.join(
            ['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1]
        )
        self.getnode = uuid.getnode(),
        self.machine = platform.machine(),
        self.node = platform.node(),
        self.platform = platform.platform(),
        self.processor = platform.processor(),
        self.release = platform.release(),
        self.system = platform.system(),
        self.version = platform.version(),
        self.uname = platform.uname(),

    @staticmethod
    def registry_airpath(agent_access_key, agent_secret_key):
        urls = 'https://dev.api.flyinglet.com/agent/registry_airpath'

        datas = {"agent_access_key": agent_access_key, "agent_secret_key": agent_secret_key}
        user_id = requests.post(url=urls, data=datas)

        return user_id


    def get_sn_registry(self):
        urls = f'https://dev.api.flyinglet.com/fcode_registry?SN={self.sn}'
        try:
            sn_registry = requests.get(url=urls).json()[0]
            fcode = sn_registry['fCode']
            return sn_registry
        except:
            return False


    @staticmethod
    def check_data(sn):
        urls = f'https://dev.api.flyinglet.com/chip_sn?SN={sn}'
        response = requests.get(url=urls)
        return response.json()


    def send_macaddress(self,fcode):
        urls = f'https://dev.api.flyinglet.com/send-device-certi'
        datas = {"mac_address": self.mac_address,
                 "authentication_timestamp": self.authentication_timestamp,
                 "getnode": self.getnode,
                 "machine": self.machine,
                 "node": self.node,
                 "platform": self.platform,
                 "processor": self.processor,
                 "release": self.release,
                 "system": self.system,
                 "version": self.version,
                 "uname": self.uname,
                 "fCode": fcode
                 }
        requests.patch(url=urls, data=datas)

    def send_airpath(self, user_id):
        urls = f'https://dev.api.flyinglet.com/Airpath'
        datas = {"SN": self.sn,
                 "SOM S/N": self.som_sn,
                 "모델명": self.name,
                 "Version": self.airpath_version,
                 "SW": self.sw,

                 "user_id": user_id,
                 "status": "등록대기"
                 }
        requests.post(url=urls, data=datas)


    def verification(self, stdscr):
        # Init curses
        stdscr = curses.initscr()

        # No echo
        curses.noecho()

        # Squence key option
        stdscr.keypad(True)

        # Set maximum retry count
        max_retry_count = 3

        # Loop until user enters correct credentials or maximum retry count is reached
        retry_count = 0
        while retry_count < max_retry_count:

            # Clear screen
            stdscr.clear()

            # Print prompt to screen
            stdscr.addstr(0, 0, 'Enter AGENT_ACCESS_KEY: ')

            # Wait for user input
            agent_access_key = ""

            while True:
                c = stdscr.getch()
                if c == ord('\n'):
                    break
                elif c == curses.ascii.BS or c == curses.KEY_BACKSPACE:
                    if len(agent_access_key.rstrip()) > 0:
                        agent_access_key = agent_access_key[:-1]
                        stdscr.addstr(0, len('Enter AGENT_ACCESS_KEY: ') + len(agent_access_key), ' ')  # 기존의 문자를 공백으로 덮어씀
                        stdscr.move(0, len('Enter AGENT_ACCESS_KEY: ') + len(agent_access_key))
                    # else:
                    #     fCode = ''
                else:
                    # Print AGENT_ACCESS_KEY to screen
                    stdscr.move(0, len('Enter AGENT_ACCESS_KEY: ') + len(agent_access_key))
                    agent_access_key += chr(c)
                    stdscr.addch(0, len('Enter AGENT_ACCESS_KEY: ') + len(agent_access_key) - 1, c)

            # Print newline character
            stdscr.clear()

            # Print prompt to screen
            stdscr.addstr(0, 0, 'Enter AGENT_SECRET_KEY: ')

            # Hide AGENT_SECRET_KEY input
            agent_secret_key = ''

            # curses.noecho()
            while True:
                c = stdscr.getch()
                if c == ord('\n'):
                    break
                elif c == curses.ascii.BS or c == curses.KEY_BACKSPACE:
                    if len(agent_secret_key.rstrip()) > 0:
                        agent_secret_key = agent_secret_key[:-1]
                        stdscr.addstr(0, len('Enter AGENT_SECRET_KEY: ') + len(agent_secret_key), ' ')  # 기존의 문자를 공백으로 덮어씀
                        stdscr.move(0, len('Enter AGENT_SECRET_KEY: ') + len(agent_secret_key))
                    else:
                        agent_secret_key = ''
                        stdscr.move(0, len('Enter AGENT_SECRET_KEY: ') + len(agent_secret_key))
                else:
                    agent_secret_key += chr(c)

                    # Print AGENT_SECRET_KEY to screen
                    stdscr.addch(0, len('Enter AGENT_SECRET_KEY: ') + len(agent_secret_key) - 1, '*')

            response = self.registry_airpath(agent_access_key, agent_secret_key)

            # 아이디 유무 확인
            if response.status_code == 200:
                self.send_airpath(response.text)
                stdscr.clear()
                stdscr.addstr(0, 0, 'verification successfully completed. The program will now exit. Please press any key.')

                # Wait for user input
                stdscr.getch()
                break

            else:
                # Increment retry count
                retry_count += 1

                # Print error message to screen
                stdscr.clear()
                stdscr.addstr(0, 0, 'Incorrect AGENT_ACCESS_KEY or AGENT_SECRET_KEY. Retry {}/{}'.format(retry_count, max_retry_count))

                # Wait for user input
                stdscr.getch()
                stdscr.clear()

            # If maximum retry count is reached, print error message to screen and wait for user input
            if retry_count == max_retry_count:
                stdscr.addstr(0, 0, 'Maximum retry count reached. Please try again later.')
                stdscr.refresh()
                stdscr.getch()
                break

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Automatically checks device authentication')
    parser.add_argument('--version', action='version', version='2.0.0', help='Show the version of the script')
    args = parser.parse_args()
    install_integrit = InstallIntegrit()
    if args.check:
        logger.info("--check 실행...")
        install_integrit.argpaser()
        logger.info("--check 완료")
    else:
        # 입력 파일 인자가 없을 경우 기본 파일을 사용
        verification = install_integrit.verification
        curses.wrapper(verification)