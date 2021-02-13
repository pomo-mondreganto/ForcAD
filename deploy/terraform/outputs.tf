output "cluster-id" {
  value = yandex_kubernetes_cluster.forcad.id
}

output "folder-id" {
  value = var.yandex_folder_id
}

output "registry-id" {
  value = yandex_container_registry.forcad.id
}
