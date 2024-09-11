variable "eks-vpc-id" {}

variable "pri-sub1-id" {}
variable "pri-sub2-id" {}

variable "pub-sub1-id" {}
variable "pub-sub2-id" {}

variable "aws_region" {
  description = "리소스가 생성될 AWS 리전"
  type        = string
  default     = "ap-northeast-1"  # 원하는 리전으로 설정
}

variable "eks_name" {
  description = "EKS 클러스터의 이름"
  type        = string
}