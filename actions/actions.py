# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Dict, Text, Any, List, Union, Type, Optional

import typing
import logging
import requests
import json
import csv

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher

#from rasa_core.trackers import (
#    DialogueStateTracker, ActionExecuted,
#    EventVerbosity)
#from rasa_core.policies.fallback import FallbackPolicy
#from rasa_core.domain import Domain
from datetime import datetime, date, time, timedelta
#from rasa_core.utils import AvailableEndpoints
#from rasa_core.tracker_store import TrackerStore

logger = logging.getLogger(__name__)
vers = 'Vers: 0.7.0, Date: Mar 18, 2019'

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def get_last_event_for(tracker, event_type: Text, action_names_to_exclude: List[Text] = None, skip: int = 0) -> Optional[Any]:

    def filter_function(e):
        has_instance = e
        if e["event"] == event_type:
            has_instance = e
        excluded = (e["event"] != event_type or ((e["event"] == event_type and ((e["parse_data"]["intent"]["name"] == "domicile") or (e["parse_data"]["intent"]["name"] == "customertype")))))
        return has_instance and not excluded

    filtered = filter(filter_function, reversed(tracker.events))
    for i in range(skip):
        next(filtered, None)

    return next(filtered, None)

def log_slots(tracker):
    #import copy
    # Log currently set slots
    logger.debug("tracker now has {} events".format(len(tracker.events)))
    prev_user_event = get_last_event_for(tracker, 'user', skip=1)
    logger.debug("event.text: {}, intent: {}, confidence: {}".format(prev_user_event["text"], prev_user_event["parse_data"]["intent"]["name"], prev_user_event["parse_data"]["intent"]["confidence"]))
    feedback_answer = tracker.get_slot("feedback")
    logger.debug("feedback: {}".format(feedback_answer))

class ActionChuck(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_chuck"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('https://api.chucknorris.io/jokes/random').text) #make an apie call
        joke = request['value'] #extract a joke from returned json response
        dispatcher.utter_message(joke) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionRon(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_ron"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('https://ron-swanson-quotes.herokuapp.com/v2/quotes').text) #make an apie call
        logger.debug("request: {}".format(request))
        joke = request[0]   + ' - Ron Swanson'
        logger.debug("joke: {}".format(joke))
        dispatcher.utter_message(joke) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionBreakingBad(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_breaking"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('https://breaking-bad-quotes.herokuapp.com/v1/quotes').text) #make an apie call
        author = request[0]['author']
        quote = request[0]['quote']
        message = quote + ' - ' + author
        #message = quote + ' - [' + author + '] (' + permalink + ')'
        dispatcher.utter_message(message) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionCorny(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_corny"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('https://official-joke-api.appspot.com/random_joke').text) #make an apie call
        author = request['punchline']
        quote = request['setup']
        message = quote + ' - ' + author
        #message = quote + ' - [' + author + '] (' + permalink + ')'
        dispatcher.utter_message(message) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionInspiring(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_inspiring"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = requests.get('https://api.forismatic.com/api/1.0/?method=getQuote&lang=en&format=json')
        if request.status_code == 200:
            logger.info("request.text: {}".format(request.text))
            resp = json.loads(request.text)
            author = resp['quoteAuthor']
            quote = resp['quoteText']
            permalink = resp['quoteLink']
            #message = quote + ' - ' + author + ' ' + permalink
            message = quote + ' - [' + author + '] (' + permalink + ')'
        else:
            message = 'quote service error (exceeded max free quotes?), error: ' + request.status_code
        #dispatcher.utter_message(message) #send the message back to the user
        dispatcher.utter_message(message) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionGeek(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_geek"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('http://quotes.stormconsultancy.co.uk/random.json').text) #make an apie call
        author = request['author']
        quote = request['quote']
        permalink = request['permalink']
        # message = quote + ' - ' + author + ' ' + permalink
        message = quote + ' - [' + author + '] (' + permalink + ')'
        dispatcher.utter_message(message) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionTrump(Action):
    def name(self):
        # define the name of the action which can then be included in training stories
        return "action_trump"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        request = json.loads(requests.get('https://api.whatdoestrumpthink.com/api/v1/quotes/random').text) #make an apie call
        joke = request['message']  + ' - Donald Trump'
        dispatcher.utter_message(joke) #send the message back to the user
        return [SlotSet("joke_type", None), SlotSet("quote_type", None)]

class ActionVersion(Action):
    def name(self):
        logger.info("ActionVersion self called")
        # define the name of the action which can then be included in training stories
        return "action_version"

    def run(self, dispatcher, tracker, domain):
        #logger.info(">>> responding with version: {}".format(vers))
        #dispatcher.utter_message(vers) #send the message back to the user
        try:
            request = json.loads(requests.get('http://rasa-x:5002/api/version').text)
        except:
            request = { "rasa-x": "", "rasa": { "production": "" }}
        logger.info(">> rasa x version response: {}".format(request['rasa-x']))
        logger.info(">> rasa version response: {}".format(request['rasa']['production']))
        dispatcher.utter_message(f"Rasa X: {request['rasa-x']}\nRasa:  {request['rasa']['production']}\nActions: {vers}")
        return []

class ActionShowSlots(Action):
    def name(self):
        logger.info("ActionVersion self called")
        # define the name of the action which can then be included in training stories
        return "action_show_slots"

    def run(self, dispatcher, tracker, domain):
        msg = "Slots:\n"
        for k, v in tracker.slots.items():
            msg += f" {k} | {v}\n"
        dispatcher.utter_message(msg)
        return []

class ActionContactInfoForm(FormAction):
    _switch_intent = False

    def name(self):
        return "contact_info_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["first_name", "middle_name", "last_name", "email", "phone"]

    def slot_mappings(self):
        return {"first_name": self.from_entity(entity="first_name", intent=["contact_info","inform_contact_info"]),
                "middle_name": self.from_entity(entity="middle_name", intent=["inform_contact_info"]),
                "last_name": self.from_entity(entity="last_name", intent=["contact_info","inform_contact_info"]),
                "email": self.from_entity(entity="email", intent=["inform_contact_info"]),
                "phone": self.from_entity(entity="phone", intent=["inform_contact_info"])
               }

    @staticmethod
    def proper_noun_slots():
        # type: () -> List[Text]
        return ["first_name",
                "middle_name",
                "last_name",
                "email",
                "phone"]

    def request_next_slot(
        self,
        dispatcher,  # type: CollectingDispatcher
        tracker,  # type: Tracker
        domain,  # type: Dict[Text, Any]
    ):
        # type: (...) -> Optional[List[Dict]]
        """Request the next slot and utter template if needed,
            else return None"""

        state = tracker.current_state()
        intent = state["latest_message"]["intent"]
        if intent["name"] != 'contact_info' and intent["name"] != 'inform_contact_info' and intent["confidence"] > 0.59:
            self._switch_intent = True
            logger.warning('request_next_slot, intent switch, abort this form')
            self.deactivate()
        else:
            self._switch_intent = False
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template(
                        "utter_ask_{}".format(slot),
                        tracker,
                        silent_fail=False,
                        **tracker.slots
                    )
                    return [SlotSet(REQUESTED_SLOT, slot)]

        # no more required slots to fill
        logger.debug("request_next_slot, No slots left to request")
        return None

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        state = tracker.current_state()
        intent = state["latest_message"]["intent"]
        logger.info("validate, slot_values: {}, intent: \n{}".format(slot_values, intent))
        #fallback = FallbackPolicy().nlu_threshold
        #logger.info("fallback: \n{}".format(fallback))

        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        logger.info("validate, slot_to_fill: {}, user text: {}".format(slot_to_fill, state["latest_message"]["text"]))

        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                if slot_to_fill in self.proper_noun_slots():
                    return[SlotSet(slot_to_fill, state["latest_message"]["text"])]
                else:
                    dispatcher.utter_message("Sorry, I could not understand your response.")

        logger.info("validate, normal exit for slot {}".format(slot_to_fill))
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        # utter submit template
        first_name = tracker.get_slot('first_name')
        middle_name = tracker.get_slot('middle_name')
        last_name = tracker.get_slot('last_name')
        email = tracker.get_slot('email')
        phone = tracker.get_slot('phone')

        logger.info("submit, first_name: {}, phone: {}".format(first_name, phone))
        
        #if penalty_location in relief_dict:
        #    utterance = relief_dict[penalty_location]
        #else:
        #    utterance = "utter_not_sure"
        #logger.info("utterance: {}".format(utterance))
        logger.info("self._switch_intent: {}".format(self._switch_intent))
        if self._switch_intent == True:
            dispatcher.utter_message("you're switching intents...")
        else:
            dispatcher.utter_template("utter_customer_info", tracker)
        # dispatcher.utter_template('utter_golfballmoved_slots', tracker)

        return [SlotSet("first_name", None), SlotSet("middle_name", None), SlotSet("last_name", None), SlotSet("email", None), SlotSet("phone", None)]
        #return [AllSlotsReset()]

class ActionMailingInfoForm(FormAction):
    def name(self):
        return "mailing_info_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["address_1", "city", "state", "zip"]

    def slot_mappings(self):
        return {"address_1": self.from_entity(entity="address_1"),
                "address_2": self.from_entity(entity="address_2"),
                "city": self.from_entity(entity="city"),
                "state": self.from_entity(entity="state"),
                "zip": self.from_entity(entity="zip"),
                "country": self.from_entity(entity="country")
               }

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        logger.info("validate, slot_values: {}".format(slot_values))

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        logger.info("validate, slot_to_fill: {}".format(slot_to_fill))
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                dispatcher.utter_message(
                    "Sorry, I could not understand your response.")

        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        # utter submit template
        address_1 = tracker.get_slot('address_1')
        address_2 = tracker.get_slot('address_2')
        city = tracker.get_slot('city')
        state = tracker.get_slot('state')
        zip = tracker.get_slot('zip')
        country = tracker.get_slot('country')

        logger.info("dispatch template, address_1: {}".format(address_1))
        
        dispatcher.utter_template("utter_mailing_info", tracker)

        return [SlotSet("address_1", None), SlotSet("address_2", None), SlotSet("city", None), SlotSet("state", None), SlotSet("zip", None), SlotSet("country", None)]
        #return [AllSlotsReset()]

class ActionOtherInfoForm(FormAction):
    def name(self):
        return "other_info_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["gender", "birthdate", "ssn"]

    def slot_mappings(self):
        return {"gender": self.from_entity(entity="gender"),
                "birthdate": self.from_entity(entity="birthdate"),
                "age": self.from_entity(entity="age"),
                "ssn": self.from_entity(entity="ssn")
               }


    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        logger.info("validate, slot_values: {}".format(slot_values))

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        logger.info("validate, slot_to_fill: {}".format(slot_to_fill))
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                dispatcher.utter_message(
                    "Sorry, I could not understand your response.")

        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        # utter submit template
        gender = tracker.get_slot('gender')
        birthdate = tracker.get_slot('birthdate')
        age = tracker.get_slot('age')
        ssn = tracker.get_slot('ssn')

        logger.info("dispatch template, gender: {}".format(gender))
        
        #if penalty_location in relief_dict:
        #    utterance = relief_dict[penalty_location]
        #else:
        #    utterance = "utter_not_sure"
        #logger.info("utterance: {}".format(utterance))
        dispatcher.utter_template("utter_other_info", tracker)
        # dispatcher.utter_template('utter_golfballmoved_slots', tracker)

        return [SlotSet("gender", None), SlotSet("birthdate", None), SlotSet("age", None), SlotSet("ssn", None)]
        #return [AllSlotsReset()]

class JokeForm(FormAction):
    def name(self):
        return "joke_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["joke_type"]

    def slot_mappings(self):
        return {"joke_type": self.from_entity(entity="joke_type")}


    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        logger.info("validate, slot_values: {}".format(slot_values))

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        logger.info("validate, slot_to_fill: {}".format(slot_to_fill))
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                dispatcher.utter_message(
                    "Sorry, I could not understand your response.")

        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        # utter submit template
        joke_type = tracker.get_slot('joke_type')

        logger.info("dispatch template, joke_type: {}".format(joke_type))

        #return [SlotSet("joke_type", None)]
        return []

class QuoteForm(FormAction):
    def name(self):
        return "quote_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["quote_type"]

    def slot_mappings(self):
        return {"quote_type": self.from_entity(entity="quote_type")}


    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot
            else reject the execution of the form action
        """
        # extract other slots that were not requested
        # but set by corresponding entity
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        logger.info("validate, slot_values: {}".format(slot_values))

        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        logger.info("validate, slot_to_fill: {}".format(slot_to_fill))
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(dispatcher, tracker, domain))
            if not slot_values:
                dispatcher.utter_message(
                    "Sorry, I could not understand your response.")

        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        # utter submit template
        quote_type = tracker.get_slot('quote_type')

        logger.info("dispatch template, quote_type: {}".format(quote_type))

        #return [SlotSet("quote_type ", None)]
        return []

def intentHistoryStr(tracker, skip, past):
    msg = ""
    prev_user_event = get_last_event_for(tracker, 'user', skip=skip)
    logger.info("event.text: {}, intent: {}, confidence: {}".format(prev_user_event["text"], prev_user_event["parse_data"]["intent"]["name"], prev_user_event["parse_data"]["intent"]["confidence"]))
    msg = "Ranked F1 scores:\n"
    msg += "* " + prev_user_event["parse_data"]["intent"]["name"] + " (" + "{:.4f}".format(prev_user_event["parse_data"]["intent"]["confidence"]) + ")\n"
    for i in range(past - 1):
        msg += "* " + prev_user_event["parse_data"]["intent_ranking"][i+1]["name"] + " (" + "{:.4f}".format(prev_user_event["parse_data"]["intent_ranking"][i+1]["confidence"]) + ")\n"
    return msg
    #msg += "* " + prev_user_event["parse_data"]["intent_ranking"][2]["name"] + " (" + "{:.4f}".format(prev_user_event["parse_data"]["intent_ranking"][2]["confidence"]) + ")\n"
    #msg += "* " + prev_user_event["parse_data"]["intent_ranking"][3]["name"] + " (" + "{:.4f}".format(prev_user_event["parse_data"]["intent_ranking"][3]["confidence"]) + ")"

class ActionLastIntent(Action):
    def name(self):
        print("ActionLastIntent self called")
        # define the name of the action which can then be included in training stories
        return "action_f1_score"

    def run(self, dispatcher, tracker, domain):
        # what your action should do
        msg = intentHistoryStr(tracker, 1, 4)
        dispatcher.utter_message(msg) #send the message back to the user
        return []

"""
DynamicForm is currently used to determine:
  - Should the user be asked for survey feedback
  - Should debug output be provided to the user
"""
class DynamicForm(FormAction):
    def name(self):
        return "dynamic_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        logger.info("DynamicForm.required_slots")
        # lookup survey to see if we need to prompt for survey
        #return ["feedback"]
        return []
        #return ["dynamic_slot"]

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        survey = tracker.get_slot('survey')
        debug = tracker.get_slot('debug')
        logger.info("DynamicForm.submit, survey: {}, debug: {} (type: {})".format(survey, debug, type(debug)))

        # if debug, utter debug info
        if debug == "1":
            msg = intentHistoryStr(tracker, 0, 4)
            dispatcher.utter_message(msg) #send the message back to the user

        # if debug, utter debug info
        if survey == "1":
            logger.info("Survey starting...")
            dispatcher.utter_template('utter_ask_feedback', tracker)
        # - utter_ask_feedback
        # * feedback
        # - action_feedback

        return []

class TimeForm(FormAction):
    """Collects sales information and adds it to the spreadsheet"""

    def name(self) -> Text:
        return "time_form"

    @staticmethod
    def required_slots(tracker) -> List[Text]:
        return [
            "time",
        ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        logger.info("slot_mappings")
        logger.info(f"time: {self.from_entity(entity='time')}")
        logger.info(f"from_time: {self.from_entity(entity='from_time')}")
        logger.info(f"to_time: {self.from_entity(entity='to_time')}")
        return {
            "from": [
                self.from_entity(entity="time"),
            ],
            "to_time": [
                self.from_entity(entity="time"),
            ],
        }

    def submit(self,
               dispatcher: CollectingDispatcher,
               tracker: Tracker,
               domain: Dict[Text, Any]) -> List[Dict]:

        import datetime

        if tracker.active_form:
            logger.info(f"tracker.active_form: {tracker.active_form}")
        else:
            intent_name = tracker.latest_message["intent"].get("name")
            logger.info(f"intent_name: {intent_name}")
            #logger.info(f"tracker.latest_message['intent']: {tracker.latest_message['intent']}

        entities = tracker.latest_message.get("entities", [])
        entities = {e["entity"]: e["value"] for e in entities}
        logger.info(f"entities: {entities}")
        entities_json = json.dumps(entities)
        #date = datetime.datetime.now().strftime("%d/%m/%Y")
        dispatcher.utter_message(text=entities_json)

        return []

class ActionDuckingTimeRange(Action):
    """Calculate time range
    ToDo:
      - Support additional grains (week, month, year)
      - Start date must be before end, when `time_from` is set, could be a later date
      - Fixup future dates
      - Handle null duckling entity, "start last weds"
      - Relative statements - "add a week"
    """ 

    def name(self) -> Text:
        return "action_time_range"

    def _extractRange(self, duckling_time, grain):
        import re

        range = dict();
        range['from'] = duckling_time
        range['to'] = duckling_time
        if grain == 'day':
            # strip timezone because of strptime limitation - https://bugs.python.org/issue22377
            # 2020-02-06T00:00:00.000-08:00
            #duckling_time = re.sub(r'\.000', r' ', duckling_time)
            #duckling_time = duckling_time[:19]
            logger.info(f"time w/o ms: {duckling_time}")
            duckling_dt = datetime.strptime(duckling_time, '%Y-%m-%dT%H:%M:%S')
            #dt = datetime.strptime("2020-03-07T00:00:00 -07:00", "%Y-%m-%dT%H:%M:%S %z")
            logger.info(f"duckling_dt: {duckling_dt}")
            dt_delta = duckling_dt + timedelta(hours=24)
            range['to'] = dt_delta.strftime('%Y-%m-%dT%H:%M:%S%z')

        return range

    def run(self, dispatcher, tracker, domain) -> List[EventType]:

        # existing slot values
        from_time = tracker.get_slot("from_time")
        to_time = tracker.get_slot("to_time")

        # duckling value
        duckling_time = tracker.get_slot("time")

        logger.info(f"duckling_time: {type(duckling_time)}, value: {duckling_time}, to_time: {to_time}, from_time: {from_time}")
        # do we have a range
        if type(duckling_time) is dict:
            from_time = tracker.get_slot("time")['from'][:19]
            to_time = tracker.get_slot("time")['to'][:19]
        else:
            logger.info(f"latest_message: {tracker.latest_message}")
            entities = tracker.latest_message.get("entities", [])
            logger.info(f"entities 1: {entities}")
            entities = {e["entity"]: e["value"] for e in entities}
            logger.info(f"entities: {entities}")
            additional_info = tracker.latest_message.get("entities", [])[0]['additional_info']
            logger.info(f"grain: {additional_info['grain']}")
            state = tracker.current_state()
            intent = state["latest_message"]["intent"]["name"]
            logger.info(f"intent: {intent}")
            if intent == 'time_from' and to_time:
                logger.info(f"setting from_time: {duckling_time[:19]}")
                from_time = duckling_time[:19]
            else:
                range = self._extractRange(duckling_time[:19], additional_info['grain'])
                from_time = range['from']
                to_time = range['to']

        #entities = {e["entity"]: e["value"] for e in entities}
        #logger.info(f"entities 2: {entities}")
        #entities_json = json.dumps(entities)

        #date = datetime.datetime.now().strftime("%d/%m/%Y")
        #dispatcher.utter_message(text=entities_json)
        logger.info(f"from: {from_time} to: {to_time}")
        dispatcher.utter_message(text=f"from: {from_time}\n  to: {to_time}")

        return [ SlotSet("from_time", from_time), SlotSet("to_time", to_time)]
