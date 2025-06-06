from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, generationFligthsDates
import random
from urllib.parse import unquote_plus


class PurchaseFlightTicket(SequentialTaskSet):  # класс с задачами (содержит основной сценарий)

    test_user_csv_file_path = './test_data/user_data_test.csv'
    test_typeSeat_csv_file_path = './test_data/typeSeat.csv'

    test_users_data = open_csv_field(test_user_csv_file_path)
    test_type_seat = open_csv_field(test_typeSeat_csv_file_path)

    def on_start(self) -> None:
        # =====================================================================================================================================================================================================
        #                                                               ||| SCRIPT 1  ДОМАШНЯЯ СТРАНИЦА |||
        # =====================================================================================================================================================================================================

        @task
        def uc01_01_getHomePage(self) -> None:
            with self.client.get(
                    '/WebTours/',
                    name='REQ01_01_1_/WebTours/',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    #  debug_stream = sys.stderr
            ) as req01_01_1_response:
                check_http_response(req01_01_1_response, "Web Tours")
                # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/welcome.pl?signOff=true',
                    name='REQ01_01_2_/cgi-bin/welcome.pl?signOff=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    # debug_stream = sys.stderr
            ) as req01_01_2_response:
                check_http_response(req01_01_2_response,
                                    "A Session ID has been created and loaded into a cookie called MSO")
                # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/nav.pl?in=home',
                    name='REQ01_01_3_/cgi-bin/nav.pl?in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    #debug_stream=sys.stderr
            ) as req01_01_3_response:
                check_http_response(req01_01_3_response, "name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req01_01_3_response.text).group(1)

        # ==========================================================================================================================================================================================================
        #                                                                    ||| SCRIPT 2 ЛОГИН |||
        # ==========================================================================================================================================================================================================

        @task
        def uc01_02_post_login(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)

            self.userLogin = self.user_data_row['userLogin']

            self.userPass = self.user_data_row['userPass']

            req_body01_02_1 = f'userSession={self.userSession}&username={self.userLogin}&password={self.userPass}&login.x=0&login.y=0&JSFormSubmit=off'

            with self.client.post(
                    '/cgi-bin/login.pl',
                    name='REQ01_02_1_/cgi-bin/login.pl',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    data=req_body01_02_1,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req01_02_1_response:
                check_http_response(req01_02_1_response, "User password was correct")

                # ==============================================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/nav.pl?page=menu&in=home',
                    name='REQ01_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req01_02_2_response:
                check_http_response(req01_02_2_response, "<title>Web Tours Navigation Bar</title>")

                # ==============================================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ01_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req01_02_3_response:
                check_http_response(req01_02_3_response,
                                    f"Welcome, <b>{self.userLogin}</b>, to the Web Tours reservation pages")

        uc01_01_getHomePage(self)
        uc01_02_post_login(self)

    # =========================================================================================================================================================================================================
    #                                                                    ||| SCRIPT 3 ОТКРЫТЬ БИЛЕТЫ |||
    # =========================================================================================================================================================================================================
    @task
    def uc01_03_openFlight(self):
        with self.client.get(
                '/cgi-bin/welcome.pl?page=search',
                name='REQ01_03_1_/cgi-bin/welcome.pl?page=search',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                # debug_stream=sys.stderr
        ) as req01_03_1_response:
            check_http_response(req01_03_1_response, "User has returned to the search page")
        # =================================================================================================================================================================================================
        with self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=flights',
                name='REQ01_03_2_/cgi-bin/nav.pl?page=menu&in=flights',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                # debug_stream=sys.stderr
        ) as req01_03_2_response:
            check_http_response(req01_03_2_response, "<title>Web Tours Navigation Bar</title>")
        # =================================================================================================================================================================================================
        with self.client.get(
                '/cgi-bin/reservations.pl?page=welcome',
                name='REQ01_03_3_/cgi-bin/reservations.pl?page=welcome',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as req01_03_3_response:
            check_http_response(req01_03_3_response, "Flight Selections")

    # =============================================================================================================================================================================================================
    #                                                                    ||| SCRIPT 4  НАЙТИ БИЛЕТЫ |||
    # ==============================================================================================================================================================================================================
    @task
    def uc01_04_findFlight(self):
        self.seat_data_row = random.choice(self.test_type_seat)

        self.seatPref = self.seat_data_row['seatPref']

        self.seatType = self.seat_data_row['seatType']

        self.depart = self.user_data_row['depart']

        self.arrive = self.user_data_row['arrive']

        date_list = generationFligthsDates()

        req_body01_04_1 = f'advanceDiscount=0&depart={self.depart}&departDate={date_list["depart_date"]}&arrive={self.arrive}&returnDate={date_list["arrive_date"]}&numPassengers=1&seatPref={self.seatPref}&seatType={self.seatType}&findFlights.x=63&findFlights.y=7&.cgifields=roundtrip&.cgifields=seatType&.cgifields=seatPref'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_04_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body01_04_1,
                catch_response=True,
               # debug_stream=sys.stderr
        ) as req01_04_1_response:
            check_http_response(req01_04_1_response, "name=\"outboundFlight\"")
        self.outboundFlight = re.search(r' name=\"outboundFlight\" value=\"(.*)\">', req01_04_1_response.text).group(1)

    # =============================================================================================================================================================================================================
    #                                                                        ||| SCRIPT 5  ВЫБОР БИЛЕТА |||
    # ==============================================================================================================================================================================================================
    @task
    def uc1_05_choiceFlight(self):
        req_body01_05_1 = f'outboundFlight={unquote_plus(self.outboundFlight)}&numPassengers=1&advanceDiscount=0&seatType={self.seatType}&seatPref={self.seatPref}&reserveFlights.x=44&reserveFlights.y=5'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_05_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body01_05_1,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as req01_05_1_response:
            check_http_response(req01_05_1_response, "Flight Reservation")

    # =============================================================================================================================================================================================================
    #                                                                        ||| SCRIPT 6  ОПЛАТА БИЛЕТА |||
    # ==============================================================================================================================================================================================================
    @task
    def uc01_06_paymentFlight(self):
        self.expDate = self.seat_data_row['expDate']

        self.creditCard = self.seat_data_row['creditCard']

        self.address1 = self.user_data_row['address1']

        self.address2 = self.user_data_row['address2']

        self.pass1 = self.user_data_row['pass1']

        req_body01_06_1 = f'firstName={self.userLogin}&lastName={self.userPass}&address1={self.address1}&address2={self.address2}&pass1={self.pass1}&creditCard={self.creditCard}&expDate={self.expDate}&oldCCOption=&numPassengers=1&seatType={self.seatType}&seatPref={self.seatPref}&outboundFlight={unquote_plus(self.outboundFlight)}&advanceDiscount=0&returnFlight=&JSFormSubmit=off&buyFlights.x=51&buyFlights.y=8&.cgifields=saveCC'

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name='REQ01_06_1_/cgi-bin/reservations.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body01_06_1,
                catch_response=True,
               # debug_stream=sys.stderr
        ) as req01_06_1_response:
            check_http_response(req01_06_1_response, f"from {self.depart} to {self.arrive}.</u></b>")


# =====================================================================================================================================================================================================================
#                                                                                 ||| END |||
# =====================================================================================================================================================================================================================
class WebToursBaseUserClass(FastHttpUser):  # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket]
