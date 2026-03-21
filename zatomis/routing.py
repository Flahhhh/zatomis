class Router:
    def __init__(self, routes=None):
        if routes is None:
            routes = {}
        self.routes = routes

    def __call__(self, link: str):
        return self.routes.get(link, None)

    def add_route(self, link: str, processor: callable):
        self.routes[link] = processor

    def set_routes(self, routes):
        self.routes = routes
