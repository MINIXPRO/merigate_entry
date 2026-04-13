# Merigate Entry — API Documentation

## Overview

Merigate Entry is a Frappe-based application that receives invoice and gate entry data from the Merigate system and stores it in the ERP.

---

## Base URL

```
https://staging.microcrispr.com
```

---

## Authentication Flow

```
Step 1: Login → Get Token
Step 2: Use Token to send data
```

---

## API Endpoints

---

### 1. Login / Register User

**Endpoint**

```
POST /api/method/merigate_entry.merigate_entry.api.merigate_api.login_user
```

**Headers**

```
Content-Type: application/json
```

**Request Body**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Success Response**

```json
{
  "message": {
    "status": "success",
    "token": "api_key:api_secret",
    "base_url": "https://staging.microcrispr.com",
    "endpoint": "https://staging.microcrispr.com/api/method/merigate_entry.merigate_entry.api.merigate_api.create_merigate_entry",
    "message": "Login successful"
  }
}
```

**Error Responses**

_User not found_

```json
{
  "message": {
    "status": "error",
    "message": "User not found. Provide first_name to create a new account."
  }
}
```

_Invalid credentials_

```json
{
  "message": {
    "status": "error",
    "message": "Invalid credentials"
  }
}
```

_No role assigned_

```json
{
  "message": {
    "status": "error",
    "message": "Access not assigned. Contact admin."
  }
}
```

---

### 2. Create / Update Merigate Entry

**Endpoint**

```
POST /api/method/merigate_entry.merigate_entry.api.merigate_api.create_merigate_entry
```

**Headers**

```
Content-Type: application/json
Authorization: token api_key:api_secret
```

**Request Body (Example)**

```json
{
  "docname": "MG-TEST-002",
  "category": "General Purchase",
  "inward_location": "Meril Main Gate",
  "gate_no": "Gate 1",
  "scan_barcode": "BC001",
  "gate_entry_no": "GE-001",
  "gate_entry_date": "2026-04-11",
  "company": "Micro Life Science Pvt Ltd",
  "name_of_supplier": "Test Supplier",
  "supplier_gst": "27AABCU9603R1ZX",
  "supplier_address": "Mumbai, Maharashtra",
  "purchase_order_no": "PO-001",
  "purchase_order_date": "2026-04-01",
  "challan_invoice_no": "INV-001",
  "challan_invoice_date": "2026-04-05",
  "bill_of_entry_no": "BOE-001",
  "bill_of_entry_date": "2026-04-06",
  "material_description": "Test Material",
  "qty_as_per_inv_challan": "10",
  "eway_bill_no": "EWB-001",
  "eway_bill_date": "2026-04-05",
  "transport_courier": "DTDC",
  "lr_airway_bill_no": "LR-001",
  "lr_airway_bill_date": "2026-04-05",
  "vehicle_type": "Truck",
  "vehicle_no": "MH-01-AB-1234",
  "driver_name": "Ramesh Kumar",
  "driver_mobile_no": "9876543210",
  "invoice_value": 125000,
  "created_by_mg": "Balamurali Selvam",
  "created_date": "2026-04-11",
  "remark": "Test entry",
  "status": "Open"
}
```

**Success Response**

```json
{
  "message": {
    "status": "success",
    "docname": "MG-TEST-002",
    "message": "Merigate Entry saved successfully"
  }
}
```

**Error Responses**

_Access denied_

```json
{
  "message": {
    "status": "error",
    "message": "Access denied. Contact admin."
  }
}
```

_Missing docname_

```json
{
  "message": {
    "status": "error",
    "message": "Merigate Doc Name is required"
  }
}
```

---

## Request Fields Reference

| Field                  | Type     | Required | Description                     |
| ---------------------- | -------- | -------- | ------------------------------- |
| docname                | Data     | Yes      | Unique document name            |
| category               | Select   | Yes      | General Purchase / Non Business |
| company                | Data     | Yes      | Company name                    |
| inward_location        | Data     | No       | Inward location                 |
| gate_no                | Data     | No       | Gate number                     |
| scan_barcode           | Data     | No       | Barcode                         |
| gate_entry_no          | Data     | No       | Entry number                    |
| gate_entry_date        | Date     | No       | YYYY-MM-DD                      |
| name_of_supplier       | Data     | No       | Supplier name                   |
| supplier_gst           | Data     | No       | GST number                      |
| supplier_address       | Data     | No       | Supplier address                |
| purchase_order_no      | Data     | No       | PO number                       |
| purchase_order_date    | Date     | No       | YYYY-MM-DD                      |
| challan_invoice_no     | Data     | No       | Invoice number                  |
| challan_invoice_date   | Date     | No       | YYYY-MM-DD                      |
| bill_of_entry_no       | Data     | No       | BOE number                      |
| bill_of_entry_date     | Date     | No       | YYYY-MM-DD                      |
| material_description   | Text     | No       | Material details                |
| qty_as_per_inv_challan | Data     | No       | Quantity                        |
| eway_bill_no           | Data     | No       | E-way bill                      |
| eway_bill_date         | Date     | No       | YYYY-MM-DD                      |
| transport_courier      | Data     | No       | Transport name                  |
| lr_airway_bill_no      | Data     | No       | LR/AWB                          |
| lr_airway_bill_date    | Date     | No       | YYYY-MM-DD                      |
| vehicle_type           | Data     | No       | Vehicle type                    |
| vehicle_no             | Data     | No       | Vehicle number                  |
| driver_name            | Data     | No       | Driver name                     |
| driver_mobile_no       | Data     | No       | Mobile number                   |
| invoice_value          | Currency | No       | Amount                          |
| created_by_mg          | Data     | No       | Created by                      |
| created_date           | Date     | No       | YYYY-MM-DD                      |
| remark                 | Text     | No       | Remarks                         |
| status                 | Select   | No       | Open / Closed / Cancelled       |
| file_url               | Data     | No       | File URL                        |

---

## User Flow

```
Login → Validate user → Check role → Generate token
→ Send data with token → Validate role → Save entry
```

---

## Role Setup

Admin must assign role manually:

```
ERP → Users → Roles → Merigate Entry User
```

Without role:

- Login will fail
- Data cannot be saved

---

## App Information

| Field        | Value                                                               |
| ------------ | ------------------------------------------------------------------- |
| App Name     | merigate_entry                                                      |
| Publisher    | Shivam Singh                                                        |
| Email        | [shivam.singh@microcrispr.com](mailto:shivam.singh@microcrispr.com) |
| License      | MIT                                                                 |
| ERP Base URL | https://staging.microcrispr.com                                     |

---

## Summary

- Role-based access control
- API-driven data entry
- Secure ERP integration
