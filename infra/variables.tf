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
  description = "CIDR allowed to reach the app (7860). Default is open to the whole internet; the Gradio app has NO authentication, so anyone can use your GPU."
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_allowed_cidr" {
  description = "CIDR allowed to SSH (22), e.g. \"203.0.113.10/32\". Required: never leave SSH open to the world."
  type        = string
}

variable "ssh_public_key_path" {
  description = "Path to the PUBLIC ssh key registered in AWS as the instance key pair. Generate it with: ssh-keygen -t ed25519 -f ~/.ssh/qwen-tts. The private key never goes through Terraform."
  type        = string
  default     = "~/.ssh/qwen-tts.pub"
}

variable "repo_url" {
  description = "HTTPS git URL of this project (public repo, so no token is needed)."
  type        = string
  default     = "https://github.com/DeveloperRafael1996/ai_qwen_tts.git"
}

variable "repo_branch" {
  description = "Branch to deploy."
  type        = string
  default     = "main"
}

variable "github_token" {
  description = "Read-only token, only needed if the repo is private (the default repo is public). NOTE: it ends up in the instance user_data (readable by anyone with EC2 access to the instance). Use a fine-grained, read-only, single-repo token."
  type        = string
  default     = ""
  sensitive   = true
}

variable "app_username" {
  description = "Username for the Gradio login."
  type        = string
  default     = "admin"
}

variable "app_password" {
  description = "Password for the Gradio login. NOTE: stored in the instance user_data (visible to anyone with EC2 access to it) and in the Terraform state."
  type        = string
  sensitive   = true

  validation {
    condition     = length(var.app_password) >= 8
    error_message = "app_password must be at least 8 characters."
  }

  # docker compose interpolates $ and treats quotes/# specially in env files.
  validation {
    condition     = can(regex("^[A-Za-z0-9!@%^&*_+=.,:;?~-]+$", var.app_password))
    error_message = "app_password may only contain letters, digits and !@%^&*_+=.,:;?~- (no spaces, quotes, $ or #)."
  }
}
