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
from dotenv import load_dotenv, set_key


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
            with open(self.env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        else:
            # .env 파일이 존재하지 않을 경우, 생성
            os.makedirs(os.path.dirname(self.env_path), exist_ok=True)
            with open(self.env_path, 'w') as f:
                f.write('# Add your environment variables here\n')
            print(f'{self.env_path} has been created.')

    def argpaser(self):
        try:
            saved_fcode = os.environ.get('FCODE').strip('\"\'')
            saved_authentication_timestamp = os.environ.get('AUTHENTICATION_TIMESTAMP').strip('\"\'')
            check_data = self.check_data(saved_fcode)
            if check_data[0]["authentication_timestamp"] == saved_authentication_timestamp:
                pass
            else:  # authentication_timestamp 가 일치하지 않을 경우 .env 내용 삭제
                with open(self.env_path, 'w') as f:
                    f.write('')
        except (Exception,):
            # authentication_timestamp 가 일치하지 않을 경우 .env 내용 삭제
            with open(self.env_path, 'w') as f:
                f.write('')

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
        response = requests.post(url=urls, data=datas)
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
                 "uname": self.uname,
                 }
        requests.patch(url=urls, data=datas)

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
                stdscr.clear()
                stdscr.addstr(0, 0, 'verification successfully completed')
                # Get MAC address
                install_integrit.get_mac_address()

                # 등록된 MAC 확인
                load_data = install_integrit.check_data(fcode)
                saved_mac = load_data[0]['mac_address']
                saved_time = load_data[0]['authentication_timestamp']
                if self.mac_address != saved_mac or os.environ.get('AUTHENTICATION_TIMESTAMP') != saved_time:
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
                        set_key(self.env_path, 'AUTHENTICATION_TIMESTAMP', str(self.authentication_timestamp))
                        os.environ['AUTHENTICATION_TIMESTAMP'] = str(self.authentication_timestamp)
                        install_integrit.send_macaddress(fcode, secretkey)

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
                set_key(self.env_path, 'FCODE', fcode)

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
    args = parser.parse_args()
    install_integrit = InstallIntegrit()
    if args.check:
        install_integrit.argpaser()
    else:
        # 입력 파일 인자가 없을 경우 기본 파일을 사용
        verification = install_integrit.verification
        curses.wrapper(verification)
