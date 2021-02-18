resource "yandex_mdb_postgresql_cluster" "forcad" {
  name        = "forcad-postgres"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.forcad.id

  config {
    version = 12
    resources {
      resource_preset_id = "s2.small"
      disk_type_id       = "network-ssd"
      disk_size          = 32
    }
  }

  database {
    name  = var.db_name
    owner = var.db_user
  }

  user {
    name     = var.db_user
    password = var.db_password
    permission {
      database_name = var.db_name
    }
  }

  host {
    zone      = var.yandex_zone
    subnet_id = yandex_vpc_subnet.forcad-resources.id
  }
}
