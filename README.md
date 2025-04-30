# 🔐 Secure Online Agenda Project

[![Ubuntu 22.04](https://img.shields.io/badge/Ubuntu-22.04-orange?logo=ubuntu)](https://ubuntu.com)
[![Security Focused](https://img.shields.io/badge/Security-By%20Design-green?logo=lock)](#security-features)
[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org)

## 📘 Overview

This project is part of the *Secure Software Design and Web Security* course.
It aims to develop a **secure online agenda** where users can manage events that include sensitive data such as descriptions, participants, and locations.

> Focus: **End-to-end security implementation using modern authentication, encryption, and secure communication standards.**

---

## 🖥️ Environment

- **OS:** Ubuntu 22.04
- **Client:** Python desktop application
- **Server:** Django backend with HTTPS support

---

## ⚙️ Installation

### 1. Install Dependencies

Run the following script:

```bash
./dependencies.sh
```

### 2. Prebuild Server

```bash
cd server
python3 manage.py runserver_plus --cert-file keys/cert.pem --key-file keys/key.pem
```

### 3. Launch Client

```bash
cd client
python3 main.py
```

---

## 🔐 Security Features

### ✅ Authentication

- Uses **display name**, **login name**, **password**, and a **secret string**.
- The **secret string + password** derive a symmetric key via PBKDF2.
- The **private key** is encrypted and stored securely.
- Challenge-response mechanism using digital signatures ensures secure login without transmitting secrets.

### ✅ Authorization

- **JWT tokens** used:
  - **Access token:** Valid for 60 minutes
  - **Refresh token:** Valid for 1 month
- Tokens are checked and refreshed automatically before each request.

### ✅ CSRF Protection

- **CSRF tokens** required for every state-changing request to the server.
- Defends against cross-site request forgery.

### ✅ Secure Data Storage

- **Hybrid encryption design**:
  - Event data encrypted with symmetric key.
  - Symmetric key encrypted with participant's **public key**.
  - Decryption only possible with corresponding **private key**.

### ✅ Secure Communication

- HTTPS with TLS enabled using self-signed certificates via `mkcert`.
- Ensures end-to-end encryption and protects against MITM attacks.

---

## 👨‍💻 Authors

- **[hzfoudia](https://gitlab.com/hzfoudia)**
- **[nboussai](https://gitlab.com/nboussai)**