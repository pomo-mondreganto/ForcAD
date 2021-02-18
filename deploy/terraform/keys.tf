resource "yandex_kms_symmetric_key" "forcad" {
  name              = "forcad-cluster"
  description       = "encryption for ForcAD k8s cluster"
  default_algorithm = "AES_128"
  rotation_period   = "8760h"
}
