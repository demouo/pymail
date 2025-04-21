# PyMail

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/pymail.svg)](https://badge.fury.io/py/pymail)
[![Downloads](https://pepy.tech/badge/pymail)](https://pepy.tech/project/pymail)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[English](#english) | [中文](#chinese)

<a name="english"></a>
# PyMail

A simple yet powerful Python error email notification tool. Automatically sends email notifications to specified recipients when program errors occur.

## Features

- Multiple recipient support
- Configurable SMTP server settings
- SSL/TLS secure connection support
- Timeout limits to prevent email flooding
- Simple decorator interface
- Environment variables and YAML configuration support
- Secure sensitive information storage using .env file

## Installation

```bash
pip install pymail-notify
```

## Configuration

You can configure email settings through:

1. Environment Variables File (Recommended):
   - Copy `.env.example` to `.env`
   - Configure your email information in `.env`
   ```bash
   # SMTP Server Configuration
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   
   # Email Account Configuration (Sensitive)
   SENDER_EMAIL=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   
   # Recipients Configuration
   EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
   ```

2. YAML Configuration File (for non-sensitive settings):
   - Copy `email_config.yaml.example` to `email_config.yaml`
   - Configure non-sensitive information in `email_config.yaml`
   - Keep sensitive information (like passwords) in `.env`

### Security Notes

1. Never commit `.env` file to version control
2. Add to `.gitignore`:
   ```
   .env
   email_config.yaml
   ```
3. Set correct permissions for `.env`:
   ```bash
   chmod 600 .env  # Owner read/write only
   ```

### Common Email Server Configurations

1. Gmail
   - SMTP Server: smtp.gmail.com
   - SSL Port: 465
   - Requires "App Password"

2. QQ Mail
   - SMTP Server: smtp.qq.com
   - SSL Port: 465
   - Requires authorization code

3. 163 Mail
   - SMTP Server: smtp.163.com
   - SSL Port: 465
   - Requires authorization code

## Usage Examples

```python
from pymail import email_on_error

@email_on_error(subject="Custom Error Subject")
def my_function():
    # Your code
    raise Exception("An error occurred")

# Or directly use EmailSender
from pymail import EmailSender

sender = EmailSender()
try:
    # Your code
except Exception as e:
    sender.send_error(str(e))
```

## Important Notes

1. For Gmail, use App Password instead of account password
2. For QQ/163 Mail, obtain authorization code
3. Use correct SMTP ports (465 for SSL, 587 for STARTTLS)
4. Default configuration limits identical error notifications (once per 5 minutes)

---

<a name="chinese"></a>
# PyMail

一个简单而强大的Python错误邮件通知工具。当程序发生错误时，自动发送邮件通知到指定的收件人列表。

## 特性

- 支持多收件人
- 可配置SMTP服务器设置
- 支持SSL/TLS安全连接
- 支持超时限制，避免邮件轰炸
- 提供简单的装饰器接口
- 支持环境变量和YAML配置文件
- 使用.env文件安全存储敏感信息

## 安装

```bash
pip install -r requirements.txt
```

## 配置

你可以通过以下方式配置邮件设置：

1. 环境变量文件（推荐）：
   - 复制 `.env.example` 到 `.env`
   - 在 `.env` 文件中配置你的邮箱信息
   ```bash
   # SMTP服务器配置
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   
   # 邮箱账号配置（敏感信息）
   SENDER_EMAIL=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   
   # 收件人配置
   EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
   ```

2. YAML配置文件（用于非敏感配置）：
   - 复制 `email_config.yaml.example` 到 `email_config.yaml`
   - 在 `email_config.yaml` 中配置非敏感信息
   - 敏感信息（如密码）请配置在 `.env` 文件中

### 安全注意事项

1. 永远不要将 `.env` 文件提交到版本控制系统
2. 在 `.gitignore` 中添加以下内容：
   ```
   .env
   email_config.yaml
   ```
3. 确保 `.env` 文件的权限设置正确：
   ```bash
   chmod 600 .env  # 只允许文件所有者读写
   ```

### 常见邮件服务器配置

1. Gmail
   - SMTP服务器：smtp.gmail.com
   - SSL端口：465
   - 需要开启"应用专用密码"

2. QQ邮箱
   - SMTP服务器：smtp.qq.com
   - SSL端口：465
   - 需要在QQ邮箱设置中获取授权码

3. 163邮箱
   - SMTP服务器：smtp.163.com
   - SSL端口：465
   - 需要在163邮箱设置中获取授权码

## 使用示例

```python
from pymail import email_on_error

@email_on_error(subject="自定义错误主题")
def my_function():
    # 你的代码
    raise Exception("发生了一个错误")

# 或者直接使用 EmailSender
from pymail import EmailSender

sender = EmailSender()
try:
    # 你的代码
except Exception as e:
    sender.send_error(str(e))
```

## 注意事项

1. 如果使用Gmail，需要使用应用专用密码而不是账户密码
2. 如果使用QQ邮箱或163邮箱，需要获取授权码
3. 确保使用正确的SMTP端口（SSL用465，STARTTLS用587）
4. 默认配置会限制相同错误的发送频率（默认5分钟内只发送一次） 