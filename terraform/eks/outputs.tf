# output "oidc_provider_arn" {
#   value = aws_iam_openid_connect_provider.oidc.arn
# }

# output "cluster_endpoint" {
#   value = aws_eks_cluster.this.endpoint
# }

# output "cluster_certificate_authority_data" {
#   value = aws_eks_cluster.this.certificate_authority[0].data
# }
# resource "aws_iam_openid_connect_provider" "oidc" {
#   client_id_list  = ["sts.amazonaws.com"]
#   thumbprint_list = [data.aws_eks_cluster.eks.cluster_certificate_authority[0].data]
#   url             = data.aws_eks_cluster.eks.identity[0].oidc[0].issuer
# }
