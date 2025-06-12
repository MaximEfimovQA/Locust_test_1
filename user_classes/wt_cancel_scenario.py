from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, processCancelRequestBody
import random
from urllib.parse import unquote_plus


class PurchaseFlightTicket(SequentialTaskSet):  # класс с задачами (содержит основной сценарий)

    test_user_csv_file_path = './test_data/user_data_test.csv'

    test_users_data = open_csv_field(test_user_csv_file_path)

    def on_start(self) -> None:
        # =====================================================================================================================================================================================================
        #                                                               ||| SCRIPT 1  ДОМАШНЯЯ СТРАНИЦА |||
        # =====================================================================================================================================================================================================

        @task
        def uc02_01_getHomePage(self) -> None:
            with self.client.get(
                    '/WebTours/',
                    name='REQ02_01_1_/WebTours/',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    #  debug_stream = sys.stderr
            ) as req02_01_1_response:
                check_http_response(req02_01_1_response, "Web Tours")
            # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/welcome.pl?signOff=true',
                    name='REQ02_01_2_/cgi-bin/welcome.pl?signOff=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    # debug_stream = sys.stderr
            ) as req02_01_2_response:
                check_http_response(req02_01_2_response,
                                    "A Session ID has been created and loaded into a cookie called MSO")
            # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/nav.pl?in=home',
                    name='REQ02_01_3_/cgi-bin/nav.pl?in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req02_01_3_response:
                check_http_response(req02_01_3_response, "name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req02_01_3_response.text).group(1)

        # ==========================================================================================================================================================================================================
        #                                                                    ||| SCRIPT 2 ЛОГИН |||
        # ==========================================================================================================================================================================================================

        @task
        def uc02_02_post_login(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)

            self.userLogin = self.user_data_row['userLogin']

            self.userPass = self.user_data_row['userPass']

            req_body02_02_1 = f'userSession={self.userSession}&username={self.userLogin}&password={self.userPass}&login.x=0&login.y=0&JSFormSubmit=off'

            with self.client.post(
                    '/cgi-bin/login.pl',
                    name='REQ02_02_1_/cgi-bin/login.pl',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    data=req_body02_02_1,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req02_02_1_response:
                check_http_response(req02_02_1_response, "User password was correct")

                # ==============================================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/nav.pl?page=menu&in=home',
                    name='REQ02_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req02_02_2_response:
                check_http_response(req02_02_2_response, "<title>Web Tours Navigation Bar</title>")

                # ==============================================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ02_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req02_02_3_response:
                check_http_response(req02_02_3_response,
                                    f"Welcome, <b>{self.userLogin}</b>, to the Web Tours reservation pages")

        uc02_01_getHomePage(self)
        uc02_02_post_login(self)

    # =========================================================================================================================================================================================================
    #                                                                    ||| SCRIPT 3 ОТКРЫТЬ БИЛЕТЫ |||
    # =========================================================================================================================================================================================================
    @task
    def uc02_03_openItinerary(self):
        with self.client.get(
                '/cgi-bin/welcome.pl?page=itinerary',
                name='REQ02_03_1_/cgi-bin/welcome.pl?page=itinerary',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                debug_stream=sys.stderr
        ) as req02_03_1_response:
            check_http_response(req02_03_1_response, "User wants the intineraries.")
        # =================================================================================================================================================================================================
        with self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=itinerary',
                name='REQ02_03_2_/cgi-bin/nav.pl?page=menu&in=itinerary',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                # debug_stream=sys.stderr
        ) as req02_03_2_response:
            check_http_response(req02_03_2_response, "<title>Web Tours Navigation Bar</title>")
        # =================================================================================================================================================================================================
        with self.client.get(
                '/cgi-bin/itinerary.pl',
                name='REQ02_03_3_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as req02_03_3_response:
            check_http_response(req02_03_3_response, "Flights List")
        self.flightsID = re.findall(r'name=\"flightID\" value=\"(.*)\"', req02_03_3_response.text)
        self.cgifields = re.findall(r'name=\".cgifields\" value=\"([0-9]{1,4})\"', req02_03_3_response.text)

    # =========================================================================================================================================================================================================
    #                                                                    ||| SCRIPT 4 УДАЛИТЬ БИЛЕТЫ |||
    # =========================================================================================================================================================================================================
    @task
    def uc02_04_deleteTickets(self) -> None:
        req_body02_04_1 = processCancelRequestBody(self.flightsID, self.cgifields)
        with self.client.post(
                '/cgi-bin/itinerary.pl',
                name='REQ02_04_1_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body02_04_1,
                catch_response=True,
                debug_stream=sys.stderr
        ) as req02_04_1_response:
            if "<b>A total of" in req02_04_1_response.text :
                # Есть список рейсов
                req02_04_1_response.success()
                match = re.search(r'<b>A total of (.*) scheduled flights\.</font></b>', req02_04_1_response.text)
                if match:
                    self.ticket_count = int(match.group(1))
            elif "No flights have been reserved" in req02_04_1_response.text:
                # Нет рейсов — считаем успешно
                req02_04_1_response.success()
            elif "database synchronization error" in req02_04_1_response.text:
                # Ошибка базы данных связанная с проблемами WEBTOURS
                req02_04_1_response.error_message = "Database sync error - tickets not deleted"
                req02_04_1_response.error_status = "error WEBTOURS"
            else:
                req02_04_1_response.failure("no ticket")  # Если это все сверху не сработало, то будет эта ошибка




# =====================================================================================================================================================================================================================
#                                                                                 ||| END |||
# =====================================================================================================================================================================================================================
class WebToursCancelUserClass(FastHttpUser):  # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.webtours_cancel.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]
