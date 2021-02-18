resource "yandex_kubernetes_cluster" "forcad" {
  name        = "forcad"
  description = "cluster for running ForcAD services"

  network_id = yandex_vpc_network.forcad.id

  master {
    version = "1.19"

    zonal {
      zone      = yandex_vpc_subnet.forcad-cluster.zone
      subnet_id = yandex_vpc_subnet.forcad-cluster.id
    }

    public_ip = true

    maintenance_policy {
      auto_upgrade = false
    }
  }

  service_account_id      = yandex_iam_service_account.forcad.id
  node_service_account_id = yandex_iam_service_account.forcad.id

  release_channel         = "RAPID"
  network_policy_provider = "CALICO"

  kms_provider {
    key_id = yandex_kms_symmetric_key.forcad.id
  }

  depends_on = [
    yandex_resourcemanager_folder_iam_member.forcad
  ]
}

resource "yandex_kubernetes_node_group" "forcad" {
  cluster_id  = yandex_kubernetes_cluster.forcad.id
  name        = "forcad"
  description = "Node group for running ForcAD services"
  version     = yandex_kubernetes_cluster.forcad.master[0].version

  instance_template {
    platform_id = "standard-v2"
    nat         = true

    resources {
      memory = 4
      cores  = 4
    }

    boot_disk {
      type = "network-ssd"
      size = 64
    }
  }

  scale_policy {
    auto_scale {
      initial = 2
      max     = 8
      min     = 1
    }
  }

  allocation_policy {
    location {
      zone      = yandex_vpc_subnet.forcad-cluster.zone
      subnet_id = yandex_vpc_subnet.forcad-cluster.id
    }
  }

  maintenance_policy {
    auto_upgrade = false
    auto_repair  = true
  }
}