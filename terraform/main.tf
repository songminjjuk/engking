module "eks-vpc" {
    source = "./vpc"
}

module "pri-cluster" {
    source = "./eks"
    eks-vpc-id = module.eks-vpc.eks-vpc-id # variables.tf 값 채우기
    pri-sub1-id = module.eks-vpc.pri-sub1-id
    pri-sub2-id = module.eks-vpc.pri-sub2-id
    pub-sub1-id = module.eks-vpc.pub-sub1-id
    pub-sub2-id = module.eks-vpc.pub-sub2-id
    # ./vpc에 있는 outputs.tf에서 출력된 값들을
    # ./eks의 variabled.tf에 넣어주는 작업
}