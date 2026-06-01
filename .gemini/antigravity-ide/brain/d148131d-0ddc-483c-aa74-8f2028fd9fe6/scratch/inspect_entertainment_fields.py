import json

filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_index_data_formdata.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

lst = data.get('Item', {}).get('List', [])
ent_items = [item for item in lst if item.get('ActivityCategoryCode') == 'entertainment']

print(f"Total entertainment items: {len(ent_items)}")
for idx, item in enumerate(ent_items):
    print(f"\n--- Item {idx} ---")
    for k, v in item.items():
        if k in ['ActivityID', 'ActivityName', 'GameTicketURL', 'ActivityCategoryCode', 'ActivityFrom', 'ActivitySDate', 'ActivityEDate', 'Date', 'GameStartDateMin', 'GameEndDateMax']:
            print(f"  {k}: {v}")
