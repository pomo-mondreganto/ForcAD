resource "yandex_vpc_network" "forcad" {
  name = "forcad"
}

resource "yandex_vpc_subnet" "forcad-cluster" {
  name           = "forcad-cluster"
  zone           = var.yandex_zone
  network_id     = yandex_vpc_network.forcad.id
  v4_cidr_blocks = ["10.11.0.0/16"]
}

resource "yandex_vpc_subnet" "forcad-resources" {
  name           = "forcad-resources"
  zone           = var.yandex_zone
  network_id     = yandex_vpc_network.forcad.id
  v4_cidr_blocks = ["10.12.0.0/16"]
}
