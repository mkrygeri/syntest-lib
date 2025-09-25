# API Request Debugging Guide

## 🎯 **Issue Identified**: Authentication Problem

Your API requests are being formed **correctly**, but you're getting **401 Unauthorized** errors because the API credentials are not set.

### **Error Evidence** 🔍
```
=== API ERROR ===
HTTP Error: 401 Client Error:  for url: https://grpc.api.kentik.com/synthetics/v202309/tests
Status Code: 401
URL: https://grpc.api.kentik.com/synthetics/v202309/tests
Method: GET
Error Response: {
  "error": "Unauthorized",
  "reasonCode": 0,
  "errxid": "d3aodv2pmv8c73833ko0"
}
```

### **Request Formation is Perfect** ✅
The debug output shows your requests are correctly formatted:
- **URL**: `https://grpc.api.kentik.com/synthetics/v202309/tests` ✅
- **Headers**: Include proper authentication headers ✅
- **Method**: Correct HTTP methods (GET, POST, etc.) ✅
- **Body**: JSON payload properly formatted ✅

## 🛠️ **New Debug Tools Added**

### **1. Enhanced Client with Debug Logging**
```python
# Enable debug logging when creating client
client = SyntheticsClient(
    email="your-email@company.com",
    api_token="your-api-token",
    debug=True  # Shows all requests and responses
)

# Or enable it later
client.enable_debug_logging(True)
```

### **2. Request Inspector Methods**
```python
# Show what a request will look like without making it
client.print_request_info("GET", "tests")
client.print_request_info("POST", "tests", data={"test": {"name": "example"}})
```

### **3. Detailed Error Logging**
Now when requests fail, you get comprehensive error information:
- HTTP status code
- Complete error response
- Request URL and method
- Full request details

### **4. Helper Scripts Created**

#### **`configure_credentials.py`** - Credential Setup Helper
```bash
python3 configure_credentials.py
```
Tests your credentials and provides setup instructions.

#### **`show_requests.py`** - Request Inspector
```bash
python3 show_requests.py
```
Shows what requests look like without making actual API calls.

#### **`test_debug_logging.py`** - Debug Feature Test
```bash
python3 test_debug_logging.py
```
Demonstrates the debug logging capabilities.

## 🔑 **How to Fix the Authentication Issue**

### **Option 1: Environment Variables** (Recommended)
```bash
export KENTIK_EMAIL="your-email@company.com"
export KENTIK_API_TOKEN="your-api-token"
```

### **Option 2: Create `.env` File**
```bash
echo 'KENTIK_EMAIL=your-email@company.com' > .env
echo 'KENTIK_API_TOKEN=your-api-token' >> .env
```

### **Option 3: Direct Code Modification**
Edit `createtests.py`:
```python
client = SyntheticsClient(
    email="your-actual-email@company.com",
    api_token="your-actual-api-token",
    debug=True
)
```

## 📋 **Getting Your API Credentials**

1. **Log into Kentik Portal**
2. **Navigate to**: Settings → API Tokens
3. **Create New Token**: Generate an API token
4. **Use**: Your login email + generated token

## 🧪 **Testing Your Setup**

Once you have credentials set:

```bash
# Test credentials
python3 configure_credentials.py

# Run your original script with debug logging
python3 createtests.py
```

## 💡 **What the Debug Output Will Show You**

With valid credentials, you'll see:

### **Request Details**
```
=== API REQUEST ===
Method: GET
URL: https://grpc.api.kentik.com/synthetics/v202309/tests
Headers: {...}
==================
```

### **Response Details**
```
=== API RESPONSE ===
Status Code: 200
Response Headers: {...}
Response Body: {
  "tests": [...]
}
====================
```

### **Error Details** (if any issues occur)
```
=== API ERROR ===
HTTP Error: 404 Not Found
Status Code: 404
URL: https://...
Method: GET
Error Response: {...}
=================
```

## 🎉 **Next Steps**

1. **Set up your credentials** using one of the methods above
2. **Test the connection** with `python3 configure_credentials.py`
3. **Run your original script** with debug logging enabled
4. **Enjoy detailed visibility** into all API interactions!

The request formation is perfect - you just need to provide valid authentication credentials!