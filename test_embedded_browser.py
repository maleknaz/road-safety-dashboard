from playwright.sync_api import sync_playwright
import json
from pathlib import Path
base='file:///mnt/data/rs_fixed/'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for file in ['Existing_road_safety_documents.html','road_safety_atlas.html','who_has_task_forces.html','Case_Studies.html','Bodies_Their_Road_Safety_Strategies.html']:
  pg=b.new_page(viewport={'width':1366,'height':880})
  errors=[]
  pg.on('pageerror',lambda e:errors.append(str(e)))
  pg.set_content(Path(file).read_text(encoding="utf-8"),wait_until="domcontentloaded",timeout=35000)
  pg.wait_for_timeout(900)
  print('\nFILE',file,'title',pg.title(),'ERRORS',errors[:4],flush=True)
  try:
   if file=='Existing_road_safety_documents.html':
    print('options',pg.locator('#countryPick option').count(),'initial summary',pg.locator('#resultsSummary, #summary').all_text_contents()[:2],flush=True)
    pg.locator('#countryPick').select_option('Sweden')
    print('SWEDEN',pg.locator('body').inner_text()[-350:], 'rows', pg.locator('.country').count(),flush=True)
    pg.locator('#countryPick').select_option('Estonia')
    print('ESTONIA',pg.locator('body').inner_text()[-350:],'rows',pg.locator('.country').count(),flush=True)
   elif file=='road_safety_atlas.html':
    print('initial',pg.locator('#searchCount').inner_text(),flush=True)
    pg.locator('#textFilter').fill('Sweden'); pg.wait_for_timeout(100)
    print('SWEDEN',pg.locator('#searchCount').inner_text(),'cards',pg.locator('#countryRows').inner_text()[:140],flush=True)
    pg.locator('#textFilter').fill('Estonia'); pg.wait_for_timeout(100)
    print('ESTONIA',pg.locator('#searchCount').inner_text(),'cards',pg.locator('#countryRows').inner_text()[:140],flush=True)
   elif file=='who_has_task_forces.html':
    pg.locator('#search').fill('Sweden');pg.wait_for_timeout(100)
    print('SWEDEN',pg.locator('body').inner_text()[-250:],flush=True)
    pg.locator('#search').fill('Estonia');pg.wait_for_timeout(100)
    print('ESTONIA',pg.locator('body').inner_text()[-250:],flush=True)
   elif file=='Case_Studies.html':
    pg.locator('#country-search').fill('Sweden');pg.wait_for_timeout(100)
    print('SWEDEN cards',pg.locator('#cards button.tile').count(),pg.locator('#cards').inner_text()[:190],flush=True)
    pg.locator('#country-search').fill('Estonia');pg.wait_for_timeout(100)
    print('ESTONIA cards',pg.locator('#cards button.tile').count(),pg.locator('#cards').inner_text()[:190],flush=True)
    opts=pg.locator('#institution-case-pick option').all_text_contents()
    if len(opts)>1:
     pg.locator('#institution-case-pick').select_option(index=1)
     print('institution table visible',pg.locator('#institution-evidence-table .institution-record:visible').count(),flush=True)
   elif file=='Bodies_Their_Road_Safety_Strategies.html':
    pg.locator('#search').fill('Sweden');pg.wait_for_timeout(100)
    print('SWEDEN',pg.locator('#showing').inner_text(),'tile',pg.locator('.country-tile').count(),flush=True)
    pg.locator('#search').fill('Estonia');pg.wait_for_timeout(100)
    print('ESTONIA',pg.locator('#showing').inner_text(),'tile',pg.locator('.country-tile').count(),flush=True)
  except Exception as ex:print('TEST ERROR',type(ex).__name__,str(ex)[:400],flush=True)
  print('late errors',errors[:5],flush=True)
  pg.close()
 b.close()
