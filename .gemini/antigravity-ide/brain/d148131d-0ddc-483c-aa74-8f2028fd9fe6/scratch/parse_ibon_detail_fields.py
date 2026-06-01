import json

filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_detail_data_formdata.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

item = data.get('Item', {})
print("Item keys:", list(item.keys()))

# Let's inspect some of the values that might contain ticket/date info
for k in ['ActivityID', 'ActivityName', 'ActivityLocation', 'ActivityIbonURL', 'ActivityBuyType']:
    print(f"  {k}: {item.get(k)}")

# Let's check sub-objects or lists in keys
for k, v in item.items():
    if isinstance(v, list) and v:
        print(f"List key: {k}, Length: {len(v)}")
        print(f"  Sample: {v[0]}")
    elif isinstance(v, dict):
        print(f"Dict key: {k}, Keys: {list(v.keys())}")
