variable "yandex_cloud_token" {
  type        = string
  description = "OAuth token for Yandex Cloud"
}

variable "yandex_cloud_id" {
  type        = string
  description = "Id of the cloud to use"
}

variable "yandex_folder_id" {
  type        = string
  description = "Id of the cloud folder to use"
}

variable "yandex_zone" {
  type        = string
  description = "Zone to use"
}

variable "db_password" {
  type        = string
  description = "Password to use with Postgres & Redis"
}

variable "db_user" {
  type        = string
  description = "User for Postgres"
}

variable "db_name" {
  type        = string
  description = "Postgres database name"
}