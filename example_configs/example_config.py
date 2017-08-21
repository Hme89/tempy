from urllib.parse import urljoin


path = "/home/user/tempy"
server_url = "http://127.0.0.1:5000/"
register_email = "mail@mail.com"


heater_pins = [27,]
sensors_id = {
    "inside":"28-XXXXXXXXXXXX",
}

register_url = urljoin(server_url, "register_client/")
info_url = urljoin(server_url, "clientinfo/")
