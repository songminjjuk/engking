
#############################
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "18.26.6"
  cluster_name = "pri-cluster"
  cluster_version = "1.29"

  vpc_id = var.eks-vpc-id

  subnet_ids = [
    var.pri-sub1-id,
    var.pri-sub2-id
    # 일단은 변수만 선언을 해두고, 나중에 vpc모듈에서 뽑아낸output값을 넣어줄꺼다
  ]

  eks_managed_node_groups = {
    pri-cluster-nodegroups = {

      min_size = 3
      max_size = 4
      desired_size = 3
      instance_types = ["m5.xlarge"]
      ###
      # labels = {
      #   "node" = "large" # 레이블 추가
      # }
    }
  }
  cluster_endpoint_private_access = true
}



# #svc 생성을 위한 webhook 포트(9443) 추가
resource "aws_security_group_rule" "allow_9443" {
  type        = "ingress"
  from_port   = 9443
  to_port     = 9443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = module.eks.node_security_group_id
}

# #생성된 파드들이 rds에 접근 가능하도록 아웃바운드 3306 허용
resource "aws_security_group_rule" "allow_3306" {
  type        = "egress"
  from_port   = 3306
  to_port     = 3306
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = module.eks.node_security_group_id
}
# resource "aws_eks_cluster" "this" {
#   name     = var.eks_name
#   role_arn = aws_iam_role.eks_role.arn

#   vpc_config {
#     subnet_ids = [var.pri-sub1-id, var.pri-sub2-id]
#   }

#   # Additional settings like version, logging, etc.
# }

data "aws_eks_cluster_auth" "this" {
  name = "pri-cluster"
}
# # pri-cluster라는 name을 갖는 클러스터의 인증정보를 가져옴.

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
  
}

# # eks 클러스터와 api 통신 및 리소스 관리하기 위한 프로바이더

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

# # 로드밸런서 컨트롤러 설치

# # 로컬 변수 선언

locals {
  lb_controller_iam_role_name        = "eks-aws-lb-ctrl"
  lb_controller_service_account_name = "aws-load-balancer-controller"
}


# # IAM ROLE 생성 및 OIDC를 통해 EKS의 SA와 연결(신뢰할 수 있는 엔터티에 등록)

module "lb_controller_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"

  create_role = true

  role_name        = local.lb_controller_iam_role_name
  role_path        = "/"
  role_description = "Used by AWS Load Balancer Controller for EKS."

  role_permissions_boundary_arn = ""

  provider_url = replace(module.eks.cluster_oidc_issuer_url, "https://", "")
  oidc_fully_qualified_subjects = [
    "system:serviceaccount:kube-system:${local.lb_controller_service_account_name}"
  ]
  oidc_fully_qualified_audiences = [
    "sts.amazonaws.com"
  ]

  depends_on = [
    module.eks
  ]
}


data "http" "iam_policy" {
  url = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json"
}
# data "local_file" "iam_policy" {
#   filename = "${path.module}/iam_policy.json" # 파일 경로 설정
# }
# # 위에서 데이터로 뽑은 정책을 role_policy를 통해 binding

resource "aws_iam_role_policy" "controller" {
  name_prefix = "AWSLoadBalancerControllerIAMPolicy"
  policy      = data.http.iam_policy.body
  # policy      = data.local_file.iam_policy.content
  role        = module.lb_controller_role.iam_role_name
}
# # 로드밸런서 컨트롤러 릴리스 생성.

# AWS 계정 ID를 가져오기 위한 데이터 소스
# data "aws_caller_identity" "current" {}

resource "helm_release" "lbc" {
  name       = "aws-load-balancer-controller"
  chart      = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  namespace  = "kube-system"

  # # 헬름에서 --set 옵션을 통해 values를 컨트롤함. --set persistence.enabled=false 처럼. --set <key>=<value> 형태로 만들어줌. 
  dynamic "set" {
    for_each = {
      "clusterName"                                               = "pri-cluster"
      "serviceAccount.create"                                     = "true"
      "serviceAccount.name"                                       = local.lb_controller_service_account_name
      "region"                                                    = "ap-northeast-1"
      "vpcId"                                                     = var.eks-vpc-id
      "image.repository"                                          = "602401143452.dkr.ecr.ap-northeast-1.amazonaws.com/amazon/aws-load-balancer-controller"
      "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn" = "arn:aws:iam::355627705292:role/eks-aws-lb-ctrl"
      # "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn" = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/eks-aws-lb-ctrl"

    }
    content {
      name  = set.key
      value = set.value
    }
  }

  depends_on = [
    resource.aws_iam_role_policy.controller
  ]
}



##########


locals {
  irsa_secret_role  = "irsa-secret-role"
  irsa_sa           = "secret-sa"
}

module "irsa_secret" {
  source = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  
  create_role = true

  role_name = local.irsa_secret_role
  role_path = "/"
  role_description = "For Secret Manager IRSA"

  role_permissions_boundary_arn = ""

  provider_url = replace(module.eks.cluster_oidc_issuer_url, "https://","")
  oidc_fully_qualified_subjects = [
    "system:serviceaccount:default:${local.irsa_sa}"
    # 네임스페이스 default
  ]
  oidc_fully_qualified_audiences = [
    "sts.amazonaws.com"
  ]
  depends_on = [ 
    module.eks
   ]
}

resource "kubernetes_service_account" "secret-sa" {
  metadata {
    name      = local.irsa_sa
    namespace = "default"
    annotations = {
      "eks.amazonaws.com/role-arn" = module.irsa_secret.iam_role_arn
    }
  }
}

# # 정책과 롤을 바인딩. 시크릿을 조회하고 값을 가져올 수 있게!

resource "aws_iam_role_policy" "irsa_secret_role_policy" {
  name = "secrets_access_policy"
  role = module.irsa_secret.iam_role_name
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}


resource "helm_release" "csi-secrets-store" {
  name       = "csi-secrets-store"
  chart      = "secrets-store-csi-driver"
  repository = "https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts"
  namespace  = "kube-system"
  
  depends_on = [
    resource.aws_iam_role_policy.irsa_secret_role_policy
  ]
}

resource "helm_release" "secrets-provider-aws" {
  name       = "secrets-provider-aws"
  chart      = "secrets-store-csi-driver-provider-aws"
  repository = "https://aws.github.io/secrets-store-csi-driver-provider-aws"
  namespace  = "kube-system"

  
  depends_on = [
    resource.aws_iam_role_policy.irsa_secret_role_policy
  ]
}

# # # ingress 배포 #


resource "kubernetes_ingress_v1" "alb" {
  metadata {
    name      = "alb-ingress"
    namespace = "default"

    annotations = {
      "alb.ingress.kubernetes.io/actions.ssl-redirect"  = jsonencode({
        "Type"          = "redirect"
        "RedirectConfig" = {
          "Protocol"  = "HTTPS"
          "Port"      = "443"
          "StatusCode" = "HTTP_301"
        }
      })
      "alb.ingress.kubernetes.io/certificate-arn"        = "arn:aws:acm:ap-northeast-1:355627705292:certificate/80ca62e7-7c66-40ec-a710-a4e8bcadfdb7"
      "alb.ingress.kubernetes.io/group.name"             = "engking-backends"
      "alb.ingress.kubernetes.io/healthcheck-path"       = "/status"
      "alb.ingress.kubernetes.io/listen-ports"           = "[{\"HTTP\":80,\"HTTPS\":443}]"
      "alb.ingress.kubernetes.io/load-balancer-name"     = "app-alb"
      "alb.ingress.kubernetes.io/scheme"                 = "internet-facing"
      "alb.ingress.kubernetes.io/target-type"            = "ip"
    }
  }

  spec {
    ingress_class_name = "alb"

    # SSL Redirect Rule
    rule {
      http {
        path {
          backend {
            service {
              name = "ssl-redirect"
              port {
                name = "use-annotation"
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    # j-back-service Rule
    rule {
      host = "jback.engking.site"
      http {
        path {
          backend {
            service {
              name = "j-back-service"
              port {
                number = 8080
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    # s-back-service Rule
    rule {
      host = "sback.engking.site"
      http {
        path {
          backend {
            service {
              name = "s-back-service"
              port {
                number = 8080
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    # n-back-service Rule
    rule {
      host = "nback.engking.site"
      http {
        path {
          backend {
            service {
              name = "n-back-service"
              port {
                number = 8000
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    # langchain-service Rule
    rule {
      host = "langchain.engking.site"
      http {
        path {
          backend {
            service {
              name = "langchain-service"
              port {
                number = 5000
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }

    # kibana-svc Rule
    rule {
      http {
        path {
          backend {
            service {
              name = "kibana-svc"
              port {
                number = 5601
              }
            }
          }
          path      = "/"
          path_type = "Prefix"
        }
      }
    }
    # rule {
    #   http {
    #     path {
    #       backend {
    #         service {
    #           name = "elasticsearch-svc"
    #           port {
    #             number = 9200
    #           }
    #         }
    #       }
    #       path      = "/"
    #       path_type = "Prefix"
    #     }
    #   }
    # }
  }
}


# resource "kubernetes_service_v1" "svc-fast" {
#   metadata {
#     name = "svc-fast"
#     namespace = "default"
#   }
#   spec {
#     selector = {
#       app = "fast"
#     }
#     session_affinity = "ClientIP"
#     # 동일한 아이피를 갖는 클라이언트는 동일한 pod에 연결시켜줌
#     port {
#       port        = 80
#       target_port = 8000
#     }

#     # type = "NodePort"
#   }
# }

# # apiVersion: secrets-store.csi.x-k8s.io/v1
# # kind: SecretProviderClass
# # metadata:
# #   name: aws-secrets
# # spec:
# #   provider: aws
# #   parameters:
# #     objects: |
# #         - objectName: "arn:aws:secretsmanager:ap-northeast-2:865577889736:secret:dev/rds-rftU0T"
# # 시크릿매니저의 시크릿을 가져다 쓸 수 있게 해줌.

# resource "kubernetes_manifest" "aws_secrets_provider_class" {
#   depends_on = [ helm_release.lbc ]
  
#   manifest = {
#     apiVersion = "secrets-store.csi.x-k8s.io/v1"
#     kind       = "SecretProviderClass"
#     metadata = {
#       name = "aws-secrets"
#       namespace = "default"
#     }
#     spec = {
#       provider = "aws"
#       parameters = {
#         objects = <<-EOT
#         - objectName: "arn:aws:secretsmanager:ap-northeast-2:865577889736:secret:dev/rds-rftU0T"
#         EOT
#       }
#     }
#   }
# }

# resource "kubernetes_deployment_v1" "fast-dep" {
#   metadata {
#     name = "fast-dep"
#     namespace = "default"
#   }

#   spec {
#     replicas = 1

#     selector {
#       match_labels = {
#         app = "fast"
#       }
#     }

#     template {
#       metadata {
#         name = "fast-pod"
#         labels = {
#           app = "fast"
#         }
#       }
      
#       spec {
#         service_account_name = "secret-sa"
#         container {
#           image = "865577889736.dkr.ecr.ap-northeast-2.amazonaws.com/fast:21"
#           name  = "fast-con"
#           volume_mount {
#             name       = "secrets-store-inline"
#             mount_path = "/mnt/secrets-store"
#             read_only  = true
#           }
#         }

#         volume {
#           name = "secrets-store-inline"
#           csi {
#             driver = "secrets-store.csi.k8s.io"
#             read_only = true
#             volume_attributes = {
#               secretProviderClass = "aws-secrets"
#             }
#           }
#         }
        
         

#         #   resources {
#         #     limits = {
#         #       cpu    = "0.5"
#         #       memory = "512Mi"
#         #     }
#         #     requests = {
#         #       cpu    = "250m"
#         #       memory = "50Mi"
#         #     }
#         #   }

#         #   liveness_probe {
#         #     http_get {
#         #       path = "/"
#         #       port = 80

#         #       http_header {
#         #         name  = "X-Custom-Header"
#         #         value = "Awesome"
#         #       }
#         #     }

#         #     initial_delay_seconds = 3
#         #     period_seconds        = 3
#         #   }
#         # }
#       }
#     }
#   }
# }