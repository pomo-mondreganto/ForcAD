resource "yandex_vpc_network" "forcad" {
  name = "forcad"
}

resource "yandex_vpc_subnet" "forcad" {
  name       = "forcad-master-network"
  zone       = var.yandex_zone
  network_id = yandex_vpc_network.forcad.id
  v4_cidr_blocks = [
    "10.11.10.0/24"
  ]
}
