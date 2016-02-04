import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
	'PMMT.settings')

import django
django.setup()

from unicodedata import normalize
from principal.models import ExternalSource, Tag

def populate():
	desc = 'Para links e documentos referentes %s'
	
	nacional = add_tag(
		name=normalize('NFKD', 'Legislação Nacional'),
		description=normalize('NFKD', desc % 'à Legislação Nacional'))
	estadual = add_tag(
		name=normalize('NFKD', 'Legislação Estadual'),
		description=normalize('NFKD', desc % 'à Legislação Estadual'))
	militar = add_tag(
		name=normalize('NFKD', 'Legislação Militar'),
		description=normalize('NFKD', desc % 'à Legislação Militar'))
	cerimonial_militar = add_tag(
		name='Cerimonial Militar',
		description= desc % 'a cerimoniais militares')

	objs = [
		{
		'name': 'CP', 
		'description': 'Código Penal', 
		'url': 'http://www.planalto.gov.br/ccivil_03/decreto-lei/del2848compilado.htm',
		'tags': [nacional]
		},
		{
		'name': 'CPP',
		'description': 'Código de Processo Penal',
		'url': 'http://www.planalto.gov.br/ccivil_03/decreto-lei/Del3689Compilado.htm',
		'tags': [nacional]
		},
		{
		'name': 'CPM',
		'description': 'Código Penal Militar',
		'url': 'http://www.planalto.gov.br/ccivil_03/decreto-lei/Del1001Compilado.htm',
		'tags': [nacional, militar]
		},
		{
		'name': 'CPPM',
		'description': 'Código de Processo Penal Militar',
		'url': 'http://www.planalto.gov.br/ccivil_03/decreto-lei/Del1002.htm',
		'tags': [nacional, militar]
		},
		{
		'name': 'CTB',
		'description': 'Código de Trânsito Brasileiro',
		'url': 'http://www.planalto.gov.br/ccivil_03/LEIS/L9503.htm',
		'tags': [nacional]
		},
		{
		'name': 'Vade Mécum 01',
		'description': 'Guarda de Honra',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/05.pdf',
		'tags': [cerimonial_militar]
		},
		{
		'name': 'Vade Mécum 02',
		'description': 'Passagem de Comando',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/06.pdf',
		'tags': [cerimonial_militar]
		},
		{
		'name': 'Vade Mécum 03',
		'description': 'Recepção de Autoridades',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/07.pdf',
		'tags': [cerimonial_militar]
		},
		{
		'name': 'Vade Mécum 09',
		'description': 'Honras Fúnebres',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/08.pdf',
		'tags': [cerimonial_militar]
		},
		{
		'name': 'RISG',
		'description': 'Regulamento Interno e dos Serviços Gerais',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/04.pdf',
		'tags': [militar]
		},
		{
		'name': 'R-200',
		'description': 'Regulamento para as Polícias e Bombeiros Militares',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR/03.pdf',
		'tags': [nacional, militar]
		},
		{
		'name': 'CC',
		'description': 'Código Civil',
		'url': 'http://www.planalto.gov.br/ccivil_03/leis/2002/L10406.htm',
		'tags': [nacional]
		},
		{
		'name': 'CPC',
		'description': 'Código de Processo Civil',
		'url': 'http://www.planalto.gov.br/ccivil_03/leis/L5869compilada.htm',
		'tags': [nacional]
		},
		{
		'name': 'Estatudo PMMT',
		'description': 'Estatuto dos Militares do Estado de Mato Grosso',
		'url': 'http://www.gestao.mt.gov.br/download.php?Op=legislacao&arquivo=LC_555-2014-107.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'Conselho de Disciplina - 1976',
		'description': 'Lei nº 3.800 de 19 de 1976: dispõe sobre o Conselho de Disciplina',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/05.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'Conselho de Justificação - 1978',
		'description': 'Lei nº 3.993 de 26 de Junho de 1978: dispõe sobre ' +
			'o Conselho de Justificação',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/06.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'Regulamento de Movimentação',
		'description': 'Decreto nº 591 de 26 de Agosto de 1980Regulamento de ' +
			'Oficiais e Praças da PMMT',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/21.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'RDPMMT',
		'description': 'Decreto nº 1.329 de 21 de Abril de 1978: aprova o ' +
			'Regulamento Disciplinar da Polícia Militar do Estado de ' +
			'Mato Grosso',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/24.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'Lei de Promoção',
		'description': 'Lei nº 9.323 de 11 de Março de 2010: dispõe sobre os ' +
			'critérios e as condições que asseguram aos Oficiais da ativa ' +
			'da Polícia Militar e do Corpo de Bombeiros Militar, mediante ' +
			'promoção, de forma seletiva, gradual e sucessiva',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/24.pdf',
		'tags': [estadual, militar]
		},
		{
		'name': 'Manual de Prisão em Flagrante',
		'description': 'Manual de Prisão em Flagrante Delito nos Crimes Militares',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/35.pdf',
		'tags': [militar]
		},
		{
		'name': 'Manual de IPM',
		'description': 'Manual de Inquérito Policia Militar - Polícia Militar ' +
			'do Estado de Minas Gerais',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/33.pdf',
		'tags': [militar]
		},
		{
		'name': 'Manual de Deserção',
		'description': 'Manual de Deserção - Antigo',
		'url': 'http://www.pm.mt.gov.br/Legislacao/MILITAR%20ESTADUAL/32.pdf',
		'tags': [militar]
		}
	]

	for obj in objs:
		es = add_externalsource(
			name=obj['name'],
			description=obj['description'],
			url=obj['url'],
			tags=obj['tags'])
	for t in Tag.objects.all():
		for es in ExternalSource.objects.filter(tags=t):
			print("- {0} - {1}".format(str(t), str(es)))


def add_tag(name, description):
	t = Tag.objects.get_or_create(
		name=name,
		description=description)[0]
	return t

def add_externalsource(name, description, url, tags):
	es = ExternalSource.objects.get_or_create(name=name)[0]
	es.description = description
	es.url = url
	for tag in tags:
		es.tags.add(tag)
	es.save()
	return es

# Start execution here!
if __name__ == '__main__':
	print("Starting population script...")
	populate()