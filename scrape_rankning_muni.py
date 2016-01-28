import re
import requests
from lxml import html, etree
import json
import pandas as pd

fixjson_re = re.compile(u'([\'"])?([a-zA-Z0-9_]+)([\'"])?:')
def fixjson (j): 
	j =  fixjson_re.sub(u'"\g<2>":', j)
	return j

indices_re = re.compile(b"var strDataGrid = \{ rows\:\[\r\n\t\t([^\n\r]*)]};\t\r\n")
indicadores_re = re.compile(b"var strDataGrid2 = \{ rows\:\[\r\n\t\t([^\n\r]*)]};\t\r\n")
	
muni_index_page = "http://ide.segeplan.gob.gt/ranking/ranking_portal/programas/rnk_grid_load.php"
muni_data = "http://ide.segeplan.gob.gt/ranking/ranking_portal/programas/rnk_chart_mun.php?prmIdMunicipio="

munis = {}
munis_xml= requests.get(muni_index_page).text
munis_root = etree.fromstring(munis_xml.encode("utf-8"))

for child in munis_root.getchildren():
	data = child.getchildren()
	id = data[0].text
	munis[id] = {
		"ranking":   data[1].text,
		"municipio": data[2].text.replace("<u>", "").replace("</u>", "").strip(),
		"departamento": data[3].text,
		"indice_gestion": float(data[4].text)
	}
	
	muni_data_raw = requests.get(muni_data + data[0].text).text
	indices = json.loads(fixjson(u"[" +  indices_re.search(muni_data_raw.encode("utf-8")).group(1).decode("utf-8") + u"]"))
	indicadores = json.loads(fixjson(u"[" + indicadores_re.search(muni_data_raw.encode("utf-8")).group(1).decode("utf-8") + u"]"))
	for ind in indices:
		munis[id][ind["data"][0].replace(",", "_")] = ind["data"][4]
	for ind in indicadores:
		munis[id][ind["data"][0].replace(",", "_")] = ind["data"][1]
	
	print("Municipio registrado: ", munis[id])
		
pd.DataFrame.from_dict(munis, orient="index").to_csv("ranking_municipios.csv")
