resource "yandex_mdb_redis_cluster" "forcad" {
  name        = "forcad-redis"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.forcad.id

  config {
    version  = "6.0"
    password = var.db_password
  }

  resources {
    resource_preset_id = "hm1.nano"
    disk_size          = 16
  }

  host {
    zone      = var.yandex_zone
    subnet_id = yandex_vpc_subnet.forcad-resources.id
  }
}
