resource "yandex_iam_service_account" "forcad" {
  name        = "forcad-manager"
  description = "service account to manage ForcAD cluster"
}

resource "yandex_resourcemanager_folder_iam_member" "forcad" {
  folder_id = var.yandex_folder_id
  role      = "editor"
  member    = "serviceAccount:${yandex_iam_service_account.forcad.id}"
}
