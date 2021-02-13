resource "yandex_container_registry" "forcad" {
  name = "forcad"
  folder_id = var.yandex_folder_id
}
