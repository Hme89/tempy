from urllib.parse import urljoin


path = "/home/user/tempy"
server_url = "https://valdres.hovrud.com"
register_email = "mail@mail.com"
log_level = "DEBUG"
debug = False


heater_pins = [27,]
sensors_id = {
    "inside":"28-XXXXXXXXXXXX",
}

register_url = urljoin(server_url, "register_client/")
info_url = urljoin(server_url, "clientinfo/")
log_url = urljoin(server_url, "pushlogs/")
