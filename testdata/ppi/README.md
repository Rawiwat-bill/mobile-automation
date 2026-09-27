# PPI test data

| ไฟล์ | commit | ใช้ทำอะไร |
|---|---|---|
| `ppi_cases.example.yaml` | ✅ | schema/contract — ค่าเป็น placeholder ทั้งหมด |
| `ppi_cases.local.yaml` | ❌ gitignore | ค่าจริงที่ approved ใช้รันจริง |

ทั้งสองไฟล์เป็น **Robot YAML variable file** — suite โหลดด้วย `Variables` โดยตรง
ไม่ต้องมี Python loader

Key ของสองไฟล์ต้องเหมือนกัน ถ้าเพิ่ม case ใหม่ให้เพิ่มใน example ด้วยเสมอ

ห้ามใส่เลขบัญชีจริง, Citizen ID, เบอร์โทร, token หรือ endpoint ใน example
