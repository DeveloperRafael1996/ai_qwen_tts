# Architecture

Deployment of the Qwen3-TTS playground on AWS, provisioned with Terraform (`infra/`).
The diagrams are Mermaid: GitHub and VS Code (Markdown preview) render them.

## 1. Infrastructure

```mermaid
flowchart LR
    user["Browser<br/>(allowed_cidr only)"]
    dev["Developer<br/>terraform apply"]

    subgraph aws["AWS - us-east-1"]
        eip["Elastic IP<br/>fixed public IP"]

        subgraph vpc["Default VPC"]
            sg{{"Security group<br/>7860 (app), 22 (SSH)<br/>source: allowed_cidr"}}

            subgraph ec2["EC2 g5.xlarge - Deep Learning AMI (Ubuntu 22.04)"]
                gpu["NVIDIA A10G 24GB<br/>driver + nvidia-container-toolkit"]
                subgraph docker["Docker Compose"]
                    app["qwen-tts-playground<br/>Gradio :7860<br/>runs as uid 1000"]
                end
                models[("./models<br/>~9.5 GB")]
                outputs[("./outputs<br/>generated WAVs")]
                ebs[("EBS gp3 100 GB")]
            end
        end
    end

    github["GitHub<br/>DeveloperRafael1996/ai_qwen_tts<br/>(public)"]
    hf["Hugging Face Hub<br/>Qwen3-TTS models<br/>(public, Apache-2.0)"]

    user -->|"http://EIP:7860"| eip --> sg --> app
    app --- gpu
    app --- models
    app --- outputs
    models --- ebs
    outputs --- ebs

    dev -.->|"creates"| aws
    ec2 -.->|"first boot: git clone"| github
    ec2 -.->|"first boot: hf download"| hf
```

## 2. First boot (`user_data`, runs once)

Log: `/var/log/qwen-setup.log`. Takes about 10-15 min before the URL responds.

```mermaid
sequenceDiagram
    autonumber
    participant TF as Terraform
    participant EC2 as EC2 instance
    participant GH as GitHub
    participant HF as Hugging Face
    participant D as Docker

    TF->>EC2: create instance + user_data
    TF->>EC2: associate Elastic IP
    EC2->>GH: git clone (branch main)
    EC2->>D: docker compose build (~6.7 GB image)
    loop 3 models
        EC2->>HF: hf download Qwen/... (anonymous)
        HF-->>EC2: weights into ./models
    end
    EC2->>D: docker compose up -d
    TF-->>TF: output url = http://EIP:7860
```

## 3. Runtime (per request)

```mermaid
flowchart LR
    B["Browser"] --> G["Gradio UI<br/>playground.py"]
    G --> T1["Voice Design<br/>1.7B (lazy load)"]
    G --> T2["Voice Clone<br/>0.6B-Base (lazy load)"]
    G --> T3["Custom Voice<br/>0.6B-CustomVoice (preloaded)"]
    T1 & T2 & T3 --> S["QwenTTSService<br/>tts_service.py"]
    S --> GPU["GPU inference<br/>bfloat16"]
    GPU --> W["WAV in ./outputs"]
    W --> G
```

## 4. Lifecycle and cost

| State | Compute (~1 $/h) | EBS + Elastic IP | Data / URL |
|---|---|---|---|
| Running | charged | charged | available |
| Stopped (`aws ec2 stop-instances`) | not charged | charged | kept, same URL |
| Destroyed (`terraform destroy`) | not charged | not charged | deleted |

Stopping and starting does not re-run `user_data`; the container comes back on its own
(`restart: unless-stopped`). Changing `user_data` in Terraform **recreates** the instance
(`user_data_replace_on_change = true`) and the disk is lost.
