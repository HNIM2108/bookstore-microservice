from locust import HttpUser, task, between

class BookstoreUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def view_books(self):
        # Giả lập hàng ngàn user lao vào xem sách cùng lúc
        self.client.get("/books/")