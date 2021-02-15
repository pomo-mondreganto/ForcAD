output "cluster-id" {
  value = yandex_kubernetes_cluster.forcad.id
}

output "folder-id" {
  value = var.yandex_folder_id
}

output "registry-id" {
  value = yandex_container_registry.forcad.id
}

output "postgres-fqdn" {
  value = yandex_mdb_postgresql_cluster.forcad.host[0].fqdn
}

output "redis-fqdn" {
  value = yandex_mdb_redis_cluster.forcad.host[0].fqdn
}
