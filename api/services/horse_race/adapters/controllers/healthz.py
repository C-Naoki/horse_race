class HealthzController:
    def get(self) -> dict:
        return {'message': 'Hello'}
