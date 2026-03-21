from .converters import json2text


class BasicResponse:
    def __init__(self, data, status: int):
        self.status = status
        self.data = data

    def get_data(self):
        return self.status, self.data


class TextResponse(BasicResponse):
    def __init__(self, data: str, status: int = 200):
        super().__init__(data, status)


class JSONResponse(BasicResponse):
    def __init__(self, data: dict, status: int = 200):
        super().__init__(json2text(data), status)


class Response(BasicResponse):
    def __init__(self, data, status: int = 200):
        if isinstance(data, dict):
            data = json2text(data)
        elif isinstance(data, int):
            data = str(data)
        super().__init__(data, status)


class NotFoundError(BasicResponse):
    def __init__(self, data: str = "Not Found", status: int = 404):
        super().__init__(data, status)


class MethodNotAllowedError(BasicResponse):
    def __init__(self, data: str = "Method Not Allowed", status: int = 405):
        super().__init__(data, status)


class BadRequestError(BasicResponse):
    def __init__(self, data: str = "Bad Request", status: int = 400):
        super().__init__(data, status)


class FuckYouResponse(BasicResponse):
    def __init__(self, data: str = "Fuck You", status: int = 488):
        super().__init__(data, status)


class ForbiddenError(BasicResponse):
    def __init__(self, data: str = "Forbidden", status: int = 403):
        super().__init__(data, status)


class InternalError(BasicResponse):
    def __init__(self, data: str = "Internal Error", status: int = 500):
        super().__init__(data, status)
