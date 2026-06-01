import json

filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_detail_data_formdata.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

item = data.get('Item', {})

print("=== Non-empty fields in detail ===")
for k, v in item.items():
    if v is not None and v != "" and v != [] and v != {}:
        val_str = str(v)
        if len(val_str) > 100:
            val_str = val_str[:100] + "..."
        print(f"  {k}: {val_str}")
