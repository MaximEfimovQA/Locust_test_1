from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field
import random
#=============================================================================================================================================================================================

class PurchaseFlightTicket(SequentialTaskSet):# класс с задачами (содержит основной сценарий)

    test_user_csv_file_path = './test_data/user_data_test.csv'

    def on_start(self) -> None:
        # =========================================================================================================================================================================================
        #                                                               |||  SCRIPT 1  |||
        # =========================================================================================================================================================================================

        @task
        def uc_01_getHomePage(self) -> None:

            self.test_users_data = open_csv_field(self.test_user_csv_file_path)

            self.client.get(
               '/WebTours/',
                name = 'REQ_01_1_/WebTours/',
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                 debug_stream = sys.stderr
            )
    #======================================================================================================================================================================================
            self.client.get(
                '/cgi-bin/welcome.pl?signOff=true',
                name='REQ_01_2_/cgi-bin/welcome.pl?signOff=true',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                debug_stream = sys.stderr
            )
    #======================================================================================================================================================================================
            with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name='REQ_01_3_/cgi-bin/nav.pl?in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                debug_stream = sys.stderr
            ) as req_01_3_response:
                check_http_response(req_01_3_response, "name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req_01_3_response.text).group(1)


    #======================================================================================================================================================================================
    #                                                                    |||  SCRIPT 2  |||
    #======================================================================================================================================================================================

        @task
        def uc_02_post_login(self) -> None:

            self.user_data_row = random.choice(self.test_users_data)

            userLogin = self.user_data_row['userLogin']

            userPass = self.user_data_row['userPass']

            req_body_02_1 = f'userSession={self.userSession}&username={userLogin}&password={userPass}&login.x=0&login.y=0&JSFormSubmit=off'

            with self.client.post(
                 '/cgi-bin/login.pl',
                     name='REQ_02_1_/cgi-bin/login.pl',
                     headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data = req_body_02_1,
                catch_response=True,
                debug_stream = sys.stderr
            ) as req_02_1_response:
                check_http_response(req_02_1_response, "User password was correct")

#======================================================================================================================================================================================

            with self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=home',
                name='REQ_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_02_1,
                catch_response=True,
                debug_stream = sys.stderr
            )   as req_02_2_response:
                check_http_response(req_02_2_response, "<title>Web Tours Navigation Bar</title>")

#=======================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    debug_stream = sys.stderr
            ) as req_02_3_response:
                check_http_response(req_02_3_response, f"Welcome, <b>{userLogin}</b>, to the Web Tours reservation pages")

#=====================================================================================================================================================================================
        uc_01_getHomePage(self)
        uc_02_post_login(self)

    @task
    def fixtest(self):
        pass

#========================================================================================================================================================================================
class WebToursBaseUserClass(FastHttpUser): # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]