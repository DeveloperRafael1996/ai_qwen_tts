variable "region" {
  description = "AWS region."
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "GPU instance type. g5.xlarge = 1x A10G (24GB, native bf16). g4dn.xlarge = T4 16GB (no native bf16)."
  type        = string
  default     = "g5.xlarge"
}

variable "volume_size_gb" {
  description = "Root EBS volume size in GB (Docker image ~7GB + models ~10GB + AMI)."
  type        = number
  default     = 100
}

variable "allowed_cidr" {
  description = "CIDR allowed to reach the app (7860) and SSH (22), e.g. \"203.0.113.10/32\". The Gradio app has no auth, so do NOT use 0.0.0.0/0 unless you accept that."
  type        = string
}

variable "key_name" {
  description = "Existing EC2 key pair name for SSH. Null = no SSH key (use it only if you need to log in)."
  type        = string
  default     = null
}

variable "repo_url" {
  description = "HTTPS git URL of this project, e.g. https://github.com/<user>/ai_qwen_tts.git"
  type        = string
}

variable "repo_branch" {
  description = "Branch to deploy."
  type        = string
  default     = "main"
}

variable "github_token" {
  description = "Read-only token, only needed if the repo is private. NOTE: it ends up in the instance user_data (readable by anyone with EC2 access to the instance). Use a fine-grained, read-only, single-repo token."
  type        = string
  default     = ""
  sensitive   = true
}
