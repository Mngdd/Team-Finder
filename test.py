# test database entries

from requests import get, post, delete

print(post('http://127.0.0.1:5000/api/users',
           json={'nickname': 'luzura',
                 'email': 'luz@owlhouse.com',
                 'password': 'witch'}).json())
print(post('http://127.0.0.1:5000/api/users',
           json={'nickname': 'mittens',
                 'email': 'amity@owlhouse.com',
                 'password': 'abomination'}).json())
print(post('http://127.0.0.1:5000/api/users',
           json={'nickname': 'hunter',
                 'email': 'hunter@owlhouse.com',
                 'password': 'wolf'}).json())
print(post('http://127.0.0.1:5000/api/users',
           json={'nickname': 'owl_lady',
                 'email': 'eda@owlhouse.com',
                 'password': 'owl_house'}).json())
print(post('http://127.0.0.1:5000/api/users',
           json={'nickname': 'willow park',
                 'email': 'willow@owlhouse.com',
                 'password': 'plant'}).json())


print(post('http://127.0.0.1:5000/api/tags',
           json={'tag': 'education'}).json())
print(post('http://127.0.0.1:5000/api/tags',
           json={'tag': 'witchcraft'}).json())
print(post('http://127.0.0.1:5000/api/tags',
           json={'tag': 'politics'}).json())


print(post('http://127.0.0.1:5000/api/projects',
           json={'team_leader': 1,
                 'title': 'Defeating Belos',
                 'description': 'Help me uncover evil plans of Emperor Belos and prevent Day of Unity.',
                 'collaborators': '5 4 2 3',
                 'tags': '3'}).json())
print(post('http://127.0.0.1:5000/api/projects',
           json={'team_leader': 2,
                 'title': 'Abomination invention club',
                 'description': 'Builders and designers alike! '
                                'Help me organise an after-school engineering club.',
                 'tags': '1'}).json())
print(post('http://127.0.0.1:5000/api/projects',
           json={'collaborators': '3 4',
                 'team_leader': 2,
                 'title': 'Getting titan\'s blood',
                 'description': 'I have organised an expedition to the Eclipse Lake.'
                                'Come with me to retrieve some titan\'s blood for interdimensional travel.'}).json())
print(post('http://127.0.0.1:5000/api/projects',
           json={'collaborators': '4',
                 'team_leader': 1,
                 'title': 'Witch apprenticeship',
                 'description': 'Looking for aspiring witches - bile sac or not - for our apprenticeship program.',
                 'tags': '1 2',
                 'archived': True}).json())
