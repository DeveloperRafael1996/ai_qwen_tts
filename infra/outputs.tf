output "url" {
  description = "Open this once the first boot finishes (~10-15 min: image build + model download)."
  value       = "http://${aws_eip.app.public_ip}:7860"
}

output "ssh" {
  description = "SSH command (private key is the one matching ssh_public_key_path)."
  value       = "ssh -i ${trimsuffix(var.ssh_public_key_path, ".pub")} ubuntu@${aws_eip.app.public_ip}"
}

output "setup_log" {
  description = "Follow the first-boot progress."
  value       = "ssh -i ${trimsuffix(var.ssh_public_key_path, ".pub")} ubuntu@${aws_eip.app.public_ip} 'tail -f /var/log/qwen-setup.log'"
}
