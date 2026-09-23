# Deep Learning AMI: ships the NVIDIA driver, Docker and nvidia-container-toolkit,
# so no driver/toolkit installation is needed.
data "aws_ami" "dlami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)*"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "app" {
  name_prefix = "qwen-tts-"
  description = "Qwen TTS playground"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Gradio app"
    from_port   = 7860
    to_port     = 7860
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.dlami.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.app.id]

  metadata_options {
    http_tokens = "required" # IMDSv2 only
  }

  root_block_device {
    volume_type = "gp3"
    volume_size = var.volume_size_gb
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    repo_url     = var.repo_url
    repo_branch  = var.repo_branch
    github_token = var.github_token
  })
  user_data_replace_on_change = true

  tags = {
    Name = "qwen-tts-playground"
  }
}

# Stable public IP so the URL survives stop/start.
resource "aws_eip" "app" {
  instance = aws_instance.app.id
  domain   = "vpc"
}
