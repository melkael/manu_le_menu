import re
import json
import requests
from message_handler import MessageHandler
from manu.models import Restaurant

ACCESS_TOKEN = None

# Il faut aussi refactor tout ce bordel (créer un fichier script à part
# et en hériter, et virer du code vers le message_handler)

# peut être que du coup si l'utilisateur met plusieurs budgets il faut le forcer à
# choisir en lui affichant un message l'y invitant


class Script():

    def __init__(self):
        self.existing_prices = {}
        self.last_messages_sent_categories = {}
        self.asked_categories = {}
        self.asked_neighborhoods = {}
        self.asked_prices = {}
        self.messageHandler = MessageHandler()

    def clean_string(self, string):
        string = re.sub(r'[^a-zA-Z ]+', '', string)
        return string

    def clean_set(self, set_to_clean):
        for string in set_to_clean:
            string_cpy = string
            set_to_clean.remove(string)
            set_to_clean.add(self.clean_string(string_cpy))
        return set_to_clean

    def set_valid_price_range(self, fbid, category, neighborhood):
        resto_set = Restaurant.objects.filter(neighborhood__icontains=neighborhood)
        arrondissement = self.get_arrondissement(resto_set[0])
        resto = (Restaurant.objects.filter(category__icontains=category).
                 filter(arrondissement=arrondissement))

        self.existing_prices[fbid] = set([])

        if resto.filter(price=1):
            self.existing_prices[fbid].add(1)
        if resto.filter(price=2):
            self.existing_prices[fbid].add(2)
        if resto.filter(price=3):
            self.existing_prices[fbid].add(3)
        if resto.filter(price=4):
            self.existing_prices[fbid].add(4)

    def compute_text_to_send(self, fbid, recevied_message):

        states = {
            'start': self.start,
            'greetings': self.greetings,
            'category': self.category,
            'neighborhood': self.neighborhood,
            'ask_price': self.ask_price,
            'answer': self.answer,
        }

        try:
            last_msg_cat = self.last_messages_sent_categories[fbid]
        except KeyError:
            self.last_messages_sent_categories[fbid] = ''
            last_msg_cat = 'start'
            pass

        return states[last_msg_cat](fbid, recevied_message)

    def compute_quick_replies(self, fbid, recevied_message):

        if self.last_messages_sent_categories[fbid] == 'ask_price':
            category = next(iter(self.clean_set(self.asked_categories[fbid])))
            neighborhood = next(iter(self.clean_set(self.asked_neighborhoods[fbid])))
            self.set_valid_price_range(fbid, category, neighborhood)
            lookup_list = ['Abordable', 'Modéré', 'Cher', 'Luxueux']
            return list(map(lambda x: lookup_list[x - 1], self.existing_prices[fbid]))
        else:
            return []

    def generate_json_to_send(self, fbid, recevied_message):
        response_texts_list = self.compute_text_to_send(fbid, recevied_message)
        quick_replies_title_list = self.compute_quick_replies(fbid, recevied_message)
        response_msg = []
        for i in range(len(response_texts_list)):
            # If you suggest replies, you do it on the last message you send your users
            if i == len(response_texts_list) - 1 and quick_replies_title_list != []:

                # If there is only one viable reply, just move on to the next message
                # and consider the user chooses automatically a valid choice
                if len(quick_replies_title_list) == 1:
                    return self.generate_json_to_send(fbid, quick_replies_title_list[0])

                quick_replies = list(map(lambda text: {'content_type': 'text',
                                                       'title': text,
                                                       'payload': '<POSTBACK_PAYLOAD>'},
                                         quick_replies_title_list))
                response_msg.append(json.dumps(
                    {"recipient": {"id": fbid},
                     "message": {"text": response_texts_list[i],
                                 "quick_replies": quick_replies}}))

            else:
                response_msg.append(
                    json.dumps(
                        {"recipient": {"id": fbid},
                         "message": {"text": response_texts_list[i]}}
                    )
                )
        return response_msg

    def repeat(self, fbid, recevied_message):
        return ['Désolé, je n\'ai pas bien compris ta demande, peux tu reformuler ?']

    def start(self, fbid, recevied_message):
        self.last_messages_sent_categories[fbid] = 'greetings'
        # name = requests.get("https://graph.facebook.com/" + fbid +
        #                     "?fields=first_name&access_token=" + ACCESS_TOKEN).json()['first_name']
        name = 'Maxou'
        return (["Salut " + name + " ! Je suis Manu Le Menu, j\'adore manger au resto et je suis \
là pour te partager mes meilleures adresses !"] + self.greetings(fbid, recevied_message))

    def greetings(self, fbid, recevied_message):
        self.last_messages_sent_categories[fbid] = 'category'
        return ['Quel genre de resto cherches-tu ?']

    def category(self, fbid, recevied_message):
        asked_category = self.messageHandler.correct_and_match(recevied_message, 'category')
        if asked_category == set([]):
            return self.repeat(fbid, recevied_message)
        else:
            self.last_messages_sent_categories[fbid] = 'neighborhood'
            self.asked_categories[fbid] = asked_category
            return ['Parfait ! Dis moi maintenant, dans quel quartier veux tu aller ?']

    def neighborhood(self, fbid, recevied_message):
        asked_neighborhood = self.messageHandler.correct_and_match(
            recevied_message, 'neighborhood')
        if asked_neighborhood == set([]):
            return self.repeat(fbid, recevied_message)
        else:
            self.last_messages_sent_categories[fbid] = 'ask_price'
            self.asked_neighborhoods[fbid] = asked_neighborhood
            return ['Super, donne moi maintenant ta fourchette de prix']

    def ask_price(self, fbid, recevied_message):
        asked_price = self.messageHandler.correct_and_match(recevied_message, 'price')
        if asked_price == set([]):
            return self.repeat(fbid, recevied_message)
        else:
            self.last_messages_sent_categories[fbid] = 'answer'
            # message handler returns a set, so thats a quick way to handle the fact
            # we always have only one (if there are two or more, it just picks one randomly)
            self.asked_prices[fbid] = next(iter(asked_price))
            return self.answer(fbid, recevied_message)

    def answer(self, fbid, received_message):
        # price, category, neighborhood = self.clean_sets(fbid, clean_prices=True)
        print ('prout prout prout')
        category = next(iter(self.clean_set(self.asked_categories[fbid])))
        neighborhood = next(iter(self.clean_set(self.asked_neighborhoods[fbid])))
        self.set_valid_price_range(fbid, category, neighborhood)

        if len(self.existing_prices[fbid]) == 0:
            self.last_messages_sent_categories[fbid] = 'category'
            return ['Désolé, je n\'ai pas de suggestion en stock ! \
Mais tu peux refaire une recherche, essayons avec un autre genre de resto !']

        return_list = self.answer_and_request_can_be_met(fbid,
                                                         neighborhood,
                                                         category,
                                                         by_neighborhood=True)
        if return_list == []:
            return_list = self.answer_and_request_can_be_met(fbid,
                                                             neighborhood,
                                                             category,
                                                             by_neighborhood=False)
        if return_list == []:
            return_list = self.answer_and_request_cannot_be_met(fbid, neighborhood, category)

        return return_list

    def answer_and_request_can_be_met(self, fbid, neighborhood, category, by_neighborhood=True):

        lookup_price_ref = {'abordable': 1, 'modere': 2, 'cher': 3, 'luxueux': 4}
        index_lookup = self.asked_prices[fbid]

        if lookup_price_ref[index_lookup] in self.existing_prices[fbid]:

            if by_neighborhood is True:
                try:
                    resto = (Restaurant.objects.filter(category__icontains=category).
                             filter(neighborhood__icontains=neighborhood).order_by('-score').
                             filter(price=lookup_price_ref[index_lookup]))
                    return (['Dans tes critères j\'aime beaucoup le ' +
                            resto[0].name + ', il est au ' + resto[0].address])
                except IndexError:
                    return []
            else:
                try:
                    resto_set = Restaurant.objects.filter(neighborhood__icontains=neighborhood)
                    arrondissement = self.get_arrondissement(resto_set[0])
                    resto = (Restaurant.objects.filter(category__icontains=category).
                             filter(arrondissement=arrondissement).order_by('-score').
                             filter(price=lookup_price_ref[index_lookup]))
                    return (['J\'adore le ' + resto[0].name + ', il est au ' + resto[0].address] + # noqa
                            ['C\'est un poil plus loin que normalement car c\'est la seule adresse de qualité qui me vienne dans tes critères']) # noqa
                except IndexError:
                    return []
        else:
            return []

    def answer_and_request_cannot_be_met(self, fbid, neighborhood, category):

        return_list = []
        return_list.append('Je n\'ai rien dans ta fourchette mais voilà quelques suggestions de qualité !') # noqa

        for price_range in self.existing_prices[fbid]:
            resto = (Restaurant.objects.filter(category__icontains=category).
                     filter(neighborhood__icontains=neighborhood).order_by('-score').
                     filter(price=price_range))

            if(price_range == 1):
                price = 'abordable'
            elif(price_range == 2):
                price = 'modéré'
            elif(price_range == 3):
                price = 'cher'
            elif(price_range == 4):
                price = 'luxueux'
            try:
                return_list.append('Il y a le ' + resto[0].name + ', il est au ' +
                                   resto[0].address + ', c\'est plutot ' + price)
            except IndexError:
                pass
        return return_list

    def get_arrondissement(self, resto_object_set):
        return resto_object_set.arrondissement
