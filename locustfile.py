from locust import HttpUser, task, between

class LocalTestUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def index_page(self):
        self.client.get("/")

    @task(1)
    def compute_page(self):
        self.client.get("/compute")
