output "url" {
  description = "Open this once the first boot finishes (~10-15 min: image build + model download)."
  value       = "http://${aws_eip.app.public_ip}:7860"
}

output "ssh" {
  description = "SSH command (only if key_name was set)."
  value       = var.key_name == null ? "no key_name set" : "ssh -i <your-key>.pem ubuntu@${aws_eip.app.public_ip}"
}

output "setup_log" {
  description = "Follow the first-boot progress."
  value       = "ssh ubuntu@${aws_eip.app.public_ip} 'tail -f /var/log/qwen-setup.log'"
}
