from dataclasses import dataclass


@dataclass
class Request:
    sender: str
    method_id: int
    method: str
    link: str
    data: str | dict = None

    def __repr__(self):
        return {
            "sender": self.sender,
            "method": self.method,
            "route": self.link,
            "data": self.data,
        }
