import asyncio
from typing import Dict
from logging import Logger, StreamHandler, DEBUG
from meshtastic import pub, serial_interface, tcp_interface, ble_interface

from .const import REQUEST_WAIT_TIME
from .routing import Router
from .request import Request
from .response import BasicResponse
from .utils import check_portnum, parse_sender, parse_packet, form_response, paginate, \
    inject_rid, check_rid_regex, PagedData, check_format, parse_paged_request, async_time_worker, \
    async_queue_sender_worker


class Zatomis:
    def __init__(self, receive_interface=None, send_interface=None, **kwargs):
        self.loop = None
        if receive_interface is None:
            receive_interface = ("serial", None)
        self.receive_interface = self._get_interface(receive_interface[0], arg=receive_interface[1])

        if send_interface is None:
            self.send_interface = self.receive_interface
        else:
            self.send_interface = self._get_interface(send_interface)

        self.router = Router()
        self.database = None

        self.logger = Logger("zatomis")
        handler = StreamHandler()
        handler.setLevel(DEBUG)
        self.logger.addHandler(handler)
        self.logger.setLevel(DEBUG)

        self.page_dict: Dict[str, PagedData] = {}
        self.packet_queue: asyncio.Queue = asyncio.Queue()
        self.page_dict_lock = asyncio.Lock()

        self.time_task = None
        self.queue_task = None
        self.running = False

    def _get_interface(self, interface_type: str, arg: str = None):
        if interface_type == "serial":
            return serial_interface.SerialInterface(devPath=arg)
        elif interface_type == "tcp":
            if arg is None:
                raise Exception("Не был получен ожидаемый аргумент для tcp-интерфейса")
            return tcp_interface.TCPInterface(arg)
        elif interface_type == "ble":
            if arg is None:
                raise Exception("Не был получен ожидаемый аргумент для ble-интерфейса")
            return ble_interface.BLEInterface(address=arg)

    async def __call__(self, packet: Dict, interface=None):
        try:
            if not check_portnum(packet):
                self.logger.info("Номер порта запроса не соответствует ожидаемому")
                return

            if not check_format(packet):
                return

            sender = parse_sender(packet)
            r_id, page, num_pages, data = parse_paged_request(packet)

            async with self.page_dict_lock:
                if r_id not in self.page_dict:
                    self.page_dict[r_id] = PagedData(num_pages)

                paged_data: PagedData = self.page_dict[r_id]
                paged_data.insert_data(page, data)

                paged_data.time_left = REQUEST_WAIT_TIME

            request = paged_data.get_request()

            if not request:
                return
            else:
                async with self.page_dict_lock:
                    if r_id in self.page_dict:
                        del self.page_dict[r_id]

            method_id, method, link, request_data = parse_packet(request)
            print("[REQUEST]: ", method, link, request_data)

            if not check_rid_regex(r_id):
                self.logger.warning("Rid приведён в неверном формате")
                return

            processor = self.router(link)
            if not processor:
                self.logger.warning(f"Путь к ресурсу не найден: {link}")
                return

            request_obj = Request(
                link=link,
                sender=sender,
                method_id=method_id,
                method=method,
                data=request_data
            )

            if request_obj.method == "COMMIT":
                await asyncio.to_thread(processor, request_obj)
                return
            else:
                raw_response = await asyncio.to_thread(processor, request_obj)#processor(request_obj)

            if isinstance(raw_response, BasicResponse):
                status, response_data = raw_response.get_data()
            elif isinstance(raw_response, tuple) and len(raw_response) == 2:
                status, response_data = raw_response
                if not isinstance(status, int) or not isinstance(response_data, str):
                    raise Exception("Типы данных, переданные контроллером не соответствуют ожидаемым")
            else:
                raise Exception("Неожиданный тип или состав ответа контроллера")

            response = form_response(status, response_data)
            response_pages = paginate(response)
            response_pages_with_rid = inject_rid(r_id, response_pages)

            print("[RESPONSE]: ", status, response_data, response_pages_with_rid)
            await self._add_queue_responses(response_pages_with_rid, sender)

        except Exception as e:
            self.logger.error(f"Возникла ошибка при выполнении: {e}")

    async def _add_queue_responses(self, response: list[str] | str, destination):
        if isinstance(response, list):
            for resp in response:
                await self.packet_queue.put((resp, destination))
        elif isinstance(response, str):
            await self.packet_queue.put((response, destination))

    def _setup_observers(self):
        pub.subscribe(self._sync_call_wrapper, "meshtastic.receive")

    def _sync_call_wrapper(self, packet, interface=None):
        try:
            asyncio.run_coroutine_threadsafe(self.__call__(packet, interface), self.loop)
        except RuntimeError:
            print("Ошибка: pubsub вызывается до запуска asyncio цикла.")

    async def _setup_workers(self):
        self.time_task = asyncio.create_task(async_time_worker(self.page_dict, self.page_dict_lock))
        self.queue_task = asyncio.create_task(async_queue_sender_worker(self.packet_queue, self.send_interface))
        print("Воркеры запущены как асинхронные задачи.")

    def _close_interface(self):
        self.receive_interface.close()
        if self.send_interface != self.receive_interface:
            self.send_interface.close()

    async def _shutdown(self):
        print("Начинаю завершение работы...")
        self.running = False

        if self.queue_task:
            await self.packet_queue.put(None)
            await self.queue_task
        if self.time_task:
            self.time_task.cancel()
            await self.time_task

        self._close_interface()
        print("Работа завершена.")

    def setup_routes(self, routes: Dict[str, callable]):
        self.router.set_routes(routes)

    async def run(self):
        self.running = True
        self.loop = asyncio.get_running_loop()
        await self._setup_workers()
        self._setup_observers()
        print("Приложение запущено")
        self.logger.info("Приложение запущено")

        try:
            while self.running:
                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\nПолучен сигнал KeyboardInterrupt. Завершение...")
        finally:
            await self._shutdown()
