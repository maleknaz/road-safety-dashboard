from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
f=sys.argv[1]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
 page=b.new_page(viewport={'width':1280,'height':900})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(Path(f).read_text(encoding='utf-8'),wait_until='domcontentloaded',timeout=40000)
 page.wait_for_timeout(200)
 print('FILE',f,'TITLE',page.title(),'errors',errors[:2],flush=True)
 if f=='Existing_road_safety_documents.html':
  for country in ['Sweden','Estonia','Canada','Sweden']:
   page.locator('#countryPick').select_option(country)
   print('COUNTRY',country,'cards',page.locator('.country').count(),'text',page.locator('.country').first.inner_text()[:90],flush=True)
 elif f=='road_safety_atlas.html':
  for country in ['Sweden','Estonia','Canada','Sweden']:
   page.locator('#textFilter').fill(country)
   print('COUNTRY',country,'count',page.locator('#searchCount').inner_text(),'sample',page.locator('#countryRows').inner_text()[:90],flush=True)
 elif f=='who_has_task_forces.html':
  for country in ['Sweden','Estonia','Canada','Sweden']:
   page.locator('#search').fill(country)
   print('COUNTRY',country,'body contains',country in page.locator('body').inner_text(),'cards',page.locator('button[data-country]:visible').count(),flush=True)
 elif f=='Case_Studies.html':
  for country in ['Sweden','Estonia','Canada','Sweden']:
   page.locator('#country-search').fill(country)
   print('COUNTRY',country,'cards',page.locator('#cards button.tile').count(),'sample',page.locator('#cards').inner_text()[:90],flush=True)
  if page.locator('#institution-case-pick option').count()>1:
   for i in [1,0,2]:
    page.locator('#institution-case-pick').select_option(index=i)
    print('SELECT profile',i,'shown',page.locator('#institution-evidence-table .institution-record:visible').count(),flush=True)
 elif f=='Bodies_Their_Road_Safety_Strategies.html':
  for country in ['Sweden','Estonia','Canada','Sweden']:
   page.locator('#search').fill(country)
   print('COUNTRY',country,'header',page.locator('#showing').inner_text(),'cards',page.locator('.country-tile').count(),flush=True)
 print('FINAL_ERRORS',errors[:3],flush=True)
 b.close()
