import asyncio
from typing import Dict

from . import PagedData


async def async_time_worker(page_dict: Dict[str, PagedData], lock: asyncio.Lock, time_step=1):
    while True:
        try:
            keys_to_check = list(page_dict.keys())
            for r_id in keys_to_check:
                async with lock:
                    if r_id in page_dict:
                        paged_data = page_dict[r_id]
                        paged_data.time_left -= time_step
                        if paged_data.time_left <= 0:
                            del page_dict[r_id]
                            print(f"[TIME_WORKER] Удалил устаревший r_id: {r_id}")
            await asyncio.sleep(time_step)
        except asyncio.CancelledError:
            print("[TIME_WORKER] Получена команда на остановку.")
            break
        except Exception as e:
            print(f"[TIME_WORKER] Ошибка: {e}")


async def async_queue_sender_worker(packet_queue: asyncio.Queue, send_interface, time_step=2):
    while True:
        try:
            item = await packet_queue.get()
            if item is None:
                print("[QUEUE_SENDER] Получен сигнал остановки.")
                break

            packet, destination = item
            print(f"[QUEUE_SENDER] Отправляю: {packet[:min(20, len(packet))]}... -> {destination}")
            await asyncio.to_thread(send_interface.sendText, packet, wantResponse=False, wantAck=False, destinationId=destination)
            #send_interface.sendText()

            packet_queue.task_done()
            await asyncio.sleep(time_step)
        except asyncio.CancelledError:
            print("[QUEUE_SENDER] Получена команда на остановку.")
            break
        except Exception as e:
            print(f"[QUEUE_SENDER] Ошибка при отправке: {e}")
            packet_queue.task_done()
