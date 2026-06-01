import json

filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_index_data_formdata.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

items = data.get('Item', {})
atap = items.get('ATAP', [])
lst = items.get('List', [])

print(f"ATAP count: {len(atap)}")
print(f"List count: {len(lst)}")

print("\n--- ATAP Sections ---")
for a in atap:
    print(f"ATAPID: {a.get('ATAPID')}, Name: {a.get('ATAPName')}, WebType: {a.get('ATAPWebType')}, Type: {a.get('ATAPType')}")
    print(f"  ActivityList: {a.get('ActivityList')[:200] if a.get('ActivityList') else None}")
    
# Categories in List
categories = {}
for item in lst:
    cat = item.get('ActivityCategoryCode')
    categories.setdefault(cat, []).append(item)

print("\n--- Unique Categories ---")
for cat, evs in categories.items():
    print(f"Category: {cat}, Count: {len(evs)}")
    print(f"  Sample titles: {[e.get('ActivityName') for e in evs[:5]]}")
