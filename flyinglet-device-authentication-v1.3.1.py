import curses
import curses.ascii
import uuid
import requests
import os
import argparse
import time
import datetime
import json
import platform
import socket

from dotenv import load_dotenv, set_key
import logging


# 로깅 레벨 설정 (예: INFO)
logging.basicConfig(level=logging.INFO)

# 로그 파일 경로 설정
version = 'v1.3.1'  # 23.09.26  check-device -> verify=False
log_file_path = f'./log/flyinglet-device-authentication-{version}.log'

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
                f.write('')
            print(f'{self.env_path} has been created.')
            logger.info("/.env 파일 생성함")

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

    def argpaser(self):
        if self.check_network_connection(retry_count=10):
            try:
                saved_fcode = os.environ.get('FCODE').strip('\"\'')
                saved_authentication_timestamp = os.environ.get('AUTHENTICATION_TIMESTAMP').strip('\"\'')
                check_data = self.check_data(saved_fcode)
                logger.info(f"[authentication_timestamp] 체크...")
                if check_data[0]["authentication_timestamp"] == saved_authentication_timestamp:
                    logger.info(f"[authentication_timestamp] 일치")
                    pass
                else:  # authentication_timestamp 가 일치하지 않을 경우 .env 내용 삭제
                    logger.info(f"[authentication_timestamp] 불일치...")
                    with open(self.env_path, 'w') as f:
                        # f.write('')
                        logger.info(".env 내용 삭제")
            except Exception as e:
                logger.error(str(e))
                # authentication_timestamp 가 일치하지 않을 경우 .env 내용 삭제
                with open(self.env_path, 'w') as f:
                    # f.write('')
                    logger.info(".env 내용 삭제")
        else:
            logger.info("네트워크 접속 실패")
            print("Network connection is not available.")
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
    def signin_device(fcode, secretkey):
        urls = 'https://dev.api.flyinglet.com/signin-device'
        datas = {"fCode": fcode, "secretKey": secretkey}
        response = requests.post(url=urls, data=datas)
        return response

    @staticmethod
    def check_data(fcode):
        urls = 'https://dev.api.flyinglet.com/check-device'
        datas = {"fCode": fcode}
        response = requests.post(url=urls, data=datas, verify=False)
        return json.loads(response.text)


    def send_macaddress(self, fcode, secretkey):
        urls = f'https://dev.api.flyinglet.com/send-device-certi'
        datas = {"fCode": fcode,
                 "secretKey": secretkey,
                 "mac_address": self.mac_address,
                 "authentication_timestamp": self.authentication_timestamp,
                 "getnode": self.getnode,
                 "machine": self.machine,
                 "node": self.node,
                 "platform": self.platform,
                 "processor": self.processor,
                 "release": self.release,
                 "system": self.system,
                 "version": self.version,
                 "uname": self.uname
                 }
        requests.patch(url=urls, data=datas)

    def verification(self, stdscr):
        logger.info("flyinglet-device-authentication 실행...")
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
            stdscr.addstr(0, 0, 'Enter F-CODE: ')

            # Wait for user input
            fcode = ""

            while True:
                c = stdscr.getch()
                if c == ord('\n'):
                    break
                elif c == curses.ascii.BS or c == curses.KEY_BACKSPACE:
                    if len(fcode.rstrip()) > 0:
                        fcode = fcode[:-1]
                        stdscr.addstr(0, len('Enter F-CODE: ') + len(fcode), ' ')  # 기존의 문자를 공백으로 덮어씀
                        stdscr.move(0, len('Enter F-CODE: ') + len(fcode))
                    # else:
                    #     fCode = ''
                else:
                    # Print F-CODE to screen
                    stdscr.move(0, len('Enter F-CODE: ') + len(fcode))
                    fcode += chr(c)
                    stdscr.addch(0, len('Enter F-CODE: ') + len(fcode) - 1, c)

            # Print newline character
            stdscr.clear()

            # Print prompt to screen
            stdscr.addstr(0, 0, 'Enter SECRET_KEY: ')

            # Hide SECRET_KEY input
            secretkey = ''

            # curses.noecho()
            while True:
                c = stdscr.getch()
                if c == ord('\n'):
                    break
                elif c == curses.ascii.BS or c == curses.KEY_BACKSPACE:
                    if len(secretkey.rstrip()) > 0:
                        secretkey = secretkey[:-1]
                        stdscr.addstr(0, len('Enter SECRET_KEY: ') + len(secretkey), ' ')  # 기존의 문자를 공백으로 덮어씀
                        stdscr.move(0, len('Enter SECRET_KEY: ') + len(secretkey))
                    else:
                        secretkey = ''
                        stdscr.move(0, len('Enter SECRET_KEY: ') + len(secretkey))
                else:
                    secretkey += chr(c)

                    # Print SECRET_KEY to screen
                    stdscr.addch(0, len('Enter SECRET_KEY: ') + len(secretkey) - 1, '*')

            response = install_integrit.signin_device(fcode, secretkey)

            # 아이디 유무 확인
            if response.status_code == 200:
                logger.info("fcode 인증 성공...")
                stdscr.clear()
                stdscr.addstr(0, 0, 'verification successfully completed')
                # Get MAC address
                install_integrit.get_mac_address()

                # 등록된 MAC 확인
                load_data = install_integrit.check_data(fcode)

                if 'mac_address' not in load_data[0] or 'authentication_timestamp' not in load_data[0] or os.environ.get('AUTHENTICATION_TIMESTAMP') is None or self.mac_address is None:
                    # Send to MongoDB
                    now = datetime.datetime.now()
                    unix_time = int(time.mktime(now.timetuple()))
                    self.authentication_timestamp = unix_time

                    # AUTHENTICATION_TIMESTAMP 환경변수에 저장
                    self.env_vars['AUTHENTICATION_TIMESTAMP'] = self.authentication_timestamp
                    set_key(self.env_path, 'AUTHENTICATION_TIMESTAMP', str(self.authentication_timestamp), quote_mode='never')
                    os.environ['AUTHENTICATION_TIMESTAMP'] = str(self.authentication_timestamp)
                    logger.info("새 환경변수 저장")
                    install_integrit.send_macaddress(fcode, secretkey)

                elif self.mac_address != load_data[0]['mac_address'] or os.environ.get('AUTHENTICATION_TIMESTAMP').strip('\"\'') != load_data[0]['authentication_timestamp']:
                    # question answer
                    question = 'Already registered F-code. Would you like to replace it with this robot? [y/n]: '
                    answer = ''

                    # Print newline character
                    stdscr.clear()

                    # Print prompt to screen
                    stdscr.addstr(0, 0, question)

                    # curses.noecho()
                    while True:
                        c = stdscr.getch()
                        if c == ord('\n'):
                            break
                        elif c == curses.ascii.BS or c == curses.KEY_BACKSPACE:
                            if len(answer.rstrip()) > 0:
                                answer = answer[:-1]
                                stdscr.addstr(0, len(question) + len(answer), ' ')  # 기존의 문자를 공백으로 덮어씀
                                stdscr.move(0, len(question) + len(answer))
                            else:
                                answer = ''
                                stdscr.move(0, len(question) + len(answer))
                        else:
                            answer += chr(c)

                            # Print SECRET_KEY to screen
                            stdscr.addch(0, len(question) + len(answer) - 1, c)

                    if answer == "y":
                        # Send to MongoDB
                        now = datetime.datetime.now()
                        unix_time = int(time.mktime(now.timetuple()))
                        self.authentication_timestamp = unix_time

                        # F-code 환경변수에 저장
                        self.env_vars['AUTHENTICATION_TIMESTAMP'] = self.authentication_timestamp
                        set_key(self.env_path, 'AUTHENTICATION_TIMESTAMP', str(self.authentication_timestamp), quote_mode='never')
                        os.environ['AUTHENTICATION_TIMESTAMP'] = str(self.authentication_timestamp)
                        install_integrit.send_macaddress(fcode, secretkey)
                        logger.info("새 환경변수로 변경")

                # Print newline character
                stdscr.refresh()
                stdscr.clear()
                stdscr.addstr(0, 0, "The task has been completed. The program will now exit. Please press any key.")

                # Wait for user input
                stdscr.getch()
                stdscr.clear()

                # F-code 환경변수에 저장
                # 1. 파일저장
                self.env_vars['FCODE'] = fcode
                set_key(self.env_path, 'FCODE', fcode, quote_mode='never')

                # 2. os레벨 저장
                os.environ['FCODE'] = fcode

                # Exit loop
                break
            else:
                # Increment retry count
                retry_count += 1

                # Print error message to screen
                stdscr.clear()
                stdscr.addstr(0, 0, 'Incorrect F-CODE or SECRET_KEY. Retry {}/{}'.format(retry_count, max_retry_count))

                # Wait for user input
                stdscr.getch()
                stdscr.clear()

        # If maximum retry count is reached, print error message to screen and wait for user input
        if retry_count == max_retry_count:
            stdscr.addstr(0, 0, 'Maximum retry count reached. Please try again later.')
            stdscr.refresh()
            stdscr.getch()


if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Automatically checks device authentication')
    parser.add_argument('--version', action='version', version=version, help='Show the version of the script')
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