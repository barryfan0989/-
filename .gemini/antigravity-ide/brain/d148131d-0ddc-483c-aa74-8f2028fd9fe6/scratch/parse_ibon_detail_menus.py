import json

filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_detail_data_formdata.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

item = data.get('Item', {})
output_filepath = "C:/Users/USER/Desktop/專題/專題/.gemini/antigravity-ide/brain/d148131d-0ddc-483c-aa74-8f2028fd9fe6/scratch/ibon_detail_parsed.txt"

with open(output_filepath, "w", encoding="utf-8") as f:
    f.write(f"ActivityID: {item.get('ActivityID')}\n")
    f.write(f"ActivityName: {item.get('ActivityName')}\n")
    f.write(f"ActivityCategoryCode: {item.get('ActivityCategoryCode')}\n")
    f.write(f"ActivitySDate: {item.get('ActivitySDate')}\n")
    f.write(f"ActivityEDate: {item.get('ActivityEDate')}\n")
    f.write(f"ActivityTicketSDate: {item.get('ActivityTicketSDate')}\n")
    f.write(f"ActivityTicketEDate: {item.get('ActivityTicketEDate')}\n")
    f.write(f"GameTicketURL: {item.get('GameTicketURL')}\n")
    
    # Let's inspect the menus
    menus = item.get('ActivityMenu', [])
    f.write(f"\nMenus count: {len(menus)}\n")
    for idx, m in enumerate(menus):
        f.write(f"\n--- Menu {idx}: {m.get('menuName')} (FieldName: {m.get('menuFieldName')}) ---\n")
        f.write(f"{m.get('menuFieldValue')[:1500]}\n")
        
print("Saved parsed detail info to ibon_detail_parsed.txt")
