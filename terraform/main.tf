module "eks-vpc" {
    source = "./vpc"
}

module "pri-cluster" {
  source      = "./eks"
  eks-vpc-id  = module.eks-vpc.eks-vpc-id 
  pri-sub1-id = module.eks-vpc.pri-sub1-id
  pri-sub2-id = module.eks-vpc.pri-sub2-id 
  pub-sub1-id = module.eks-vpc.pub-sub1-id 
  pub-sub2-id = module.eks-vpc.pub-sub2-id
  eks_name = "pri-cluster"
}

# # IAM role setup for ALB controller
# module "lb_role" {
#   source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
#   role_name = "alb_ingress_role"
#   attach_load_balancer_controller_policy = false

#   oidc_providers = {
#     main = {
#       provider_arn               = module.pri-cluster.oidc_provider_arn
#       namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
#     }
#   }
# }
# # Define the service account for ALB Ingress Controller
# resource "kubernetes_service_account" "service-account" {
#   metadata {
#     name      = "aws-load-balancer-controller"
#     namespace = "kube-system"
#     labels = {
#       "app.kubernetes.io/name" = "aws-load-balancer-controller"
#       "app.kubernetes.io/component" = "controller"
#     }
#     annotations = {
#       "eks.amazonaws.com/role-arn" = module.lb_role.arn
#       "eks.amazonaws.com/sts-regional-endpoints" = "true"
#     }
#   }
# }
# # Helm provider configuration
# provider "helm" {
#   kubernetes {
#     host                   = module.pri-cluster.cluster_endpoint
#     cluster_ca_certificate = base64decode(module.pri-cluster.cluster_certificate_authority_data)
#     exec {
#       api_version = "client.authentication.k8s.io/v1alpha1"
#       args        = ["eks", "get-token", "--cluster-name", "pri-cluster"]
#       command     = "aws"
#     }
#   }
# }

# # Install ALB Ingress Controller using Helm
# resource "helm_release" "aws_lb_controller" {
#   name       = "aws-load-balancer-controller"
#   repository = "https://aws.github.io/eks-charts"
#   chart      = "aws-load-balancer-controller"
#   namespace  = "kube-system"
#   depends_on = [
#     kubernetes_service_account.service-account
#   ]

#   set {
#     name  = "region"
#     value = module.eks-vpc.region
#   }

#   set {
#     name  = "vpcId"
#     value = module.eks-vpc.eks-vpc-id
#   }

#   set {
#     name  = "image.repository"
#     value = "602401143452.dkr.ecr.${module.eks-vpc.region}.amazonaws.com/amazon/aws-load-balancer-controller"
#   }

#   set {
#     name  = "serviceAccount.create"
#     value = "false"
#   }

#   set {
#     name  = "serviceAccount.name"
#     value = "aws-load-balancer-controller"
#   }

#   set {
#     name  = "clusterName"
#     value = "pri-cluster"
#   }
# }

# # Add output for ALB controller status
# output "alb_controller_status" {
#   description = "The status of ALB Ingress Controller"
#   value       = helm_release.aws_lb_controller.status
# }