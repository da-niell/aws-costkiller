# 💸 CostKiller – Asesino de Recursos Ociosos en AWS

## 🚀 ¿Qué es CostKiller?

CostKiller es una herramienta automatizada que escanea tu cuenta de AWS en busca de recursos ociosos y te genera un informe del **costo potencialmente ahorrado** si los eliminás.

Este proyecto está pensado como un ejemplo completo **DevOps-friendly** con:

- 🧠 **Python + boto3** para escanear servicios de AWS
- 🐳 **Docker** para empaquetar el analizador
- ☁️ **Lambda** para correrlo serverless
- ⚙️ **Terraform** para desplegar la infraestructura
- 🤖 **GitHub Actions** para escaneos automáticos periódicos
- 📊 **Frontend simple** para visualizar el informe de ahorro

---

## 📂 Estructura del proyecto
```
costkiller/ 
├── .github/workflows/ → CI/CD con GitHub Actions 
├── infra/terraform/ → Infraestructura con Terraform 
├── lambda/ → Código Lambda (Python + boto3) 
├── frontend/ → Visualización web del informe 
├── scripts/ → Scripts para testing local 
├── data/ → Reportes generados (costos) 
└── README.md
```

---

## ⚙️ Cómo funciona

1. **Lambda** escanea los servicios AWS que elijas (EC2, S3, EBS, Lambda, etc.)
2. Detecta recursos sin uso reciente o sin actividad
3. Calcula un estimado del costo mensual de esos recursos
4. Genera un reporte JSON (y se puede visualizar en la web)
5. GitHub Actions lo corre automáticamente cada X días

---

## 📦 Requisitos

- Cuenta de AWS con permisos para describir recursos
- Python 3.9+
- AWS CLI configurado
- Terraform 1.4+
- Node.js (opcional para frontend)

---

## 🛠️ Cómo empezar

### 1. Clonar el proyecto
```bash
git clone https://github.com/tu-usuario/costkiller.git
cd costkiller
```

### 2. Testear localmente
```bash
cd lambda
pip install -r requirements.txt
python ../scripts/run_scan_local.py
```

### 3. Desplegar con Terraform
```bash
cd infra/terraform
terraform init
terraform apply
```

---

## 🔐 Seguridad
CostKiller **no elimina recursos automáticamente**, solo los detecta y recomienda qué podés borrar.
Todo corre bajo el principio de read-only access salvo que vos decidas lo contrario.

---

## 🧼 Buenas Prácticas para Mantener el Proyecto Gratis
💡 Este proyecto puede mantenerse dentro del Free Tier de AWS si seguís estas simples recomendaciones:

### 🕒 1. Invocación de Lambda
- ✅ Ejecutá la función máximo 1 vez por día.
- ⛔ No configures ejecuciones cada pocos minutos (innecesario y acumulativo).

```bash
# Ejemplo: Ejecutar 1 vez por día a las 03:00 UTC
schedule_expression = "cron(0 3 * * ? *)"
```

### 📊 2. Retención de Logs en CloudWatch
- ✅ Configurá una retención de logs corta (7 o 14 días).
- Esto evita acumulación y posibles cargos por almacenamiento.

```bash
resource "aws_cloudwatch_log_group" "costkiller_log" {
  name              = "/aws/lambda/${aws_lambda_function.costkiller.function_name}"
  retention_in_days = 7
}
```

### ☁️ 3. Almacenamiento de reportes en S3
- ✅ Usá un bucket exclusivo para este proyecto (más control).
- ✅ Aplicá una regla de ciclo de vida para borrar archivos viejos automáticamente.

```bash
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "expire-old-reports"
    status = "Enabled"

    expiration {
      days = 30
    }

    filter {}
  }
}
```

### 🧹 4. Limpieza del entorno
- ✅ Si el proyecto es temporal, ejecutá terraform destroy al finalizar.
- ✅ Usá terraform plan antes de aplicar cambios para evitar sorpresas.

### 🎛️ 5. Revisión mensual
Revisá en AWS Cost Explorer si todo sigue bajo $0.

---

## 💡 Roadmap
- Soporte para EC2, S3, EBS y Lambda
- Escaneo multi-región
- Dashboard dinámico con React
- Bot de Slack con recomendaciones automáticas
- Modo “Terminator”: borrar recursos bajo ciertas condiciones

---
