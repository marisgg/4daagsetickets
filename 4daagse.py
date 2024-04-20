import json
import time
import requests
import os
import platform
import functools
from datetime import datetime
import webbrowser

if platform.system().lower() == "windows":
    print("INFO: detected Windows OS.")
    make_sound = lambda : print('\a')
elif platform.system().lower() == "linux":
    print("INFO: detected Linux OS. Requires installation of NumPy and sounddevice.")
    import numpy as np
    import sounddevice as sd

    def bip(freq, dur, a=0, d=0, s=1, r=0):
        t=np.arange(0,dur,1/44100)
        env=np.interp(t, [0, a, (a+d), dur-r, dur], [0, 1, s, s, 0])
        sound=np.sin(2*np.pi*freq*t)*env
        sd.play(sound, samplerate=44100)

    make_sound = lambda : bip(880,0.4, a=0, d=0.24, s=0.28, r=0.09)
elif platform.system().lower() == "darwin":
    print("INFO: detected MacOS. Sound is untested.")
    make_sound = lambda : print('\a')
else:
    raise ValueError("Don't understand the platform.")

print("Testing sound:")

make_sound()

URL = "https://atleta.cc/e/zRLhVgiDSdOK/resale"
GRAPHQL_URL = "https://atleta.cc/api/graphql"

graph = {
    "operationName" : "GetRegistrationsForSale",
    "variables" : {
        "id": "zRLhVgiDSdOK",
        "tickets": None,
        "limit": 10
    },
    "query" : """query GetRegistrationsForSale($id: ID!, $tickets: [String!], $limit: Int!) {
  event(id: $id) {
    id
    registrations_for_sale_count
    filtered_registrations_for_sale_count: registrations_for_sale_count(
      tickets: $tickets
    )
    sold_registrations_count
    tickets_for_resale {
      id
      title
      __typename
    }
    registrations_for_sale(tickets: $tickets, limit: $limit) {
      id
      ticket {
        id
        title
        __typename
      }
      ticket {
        id
        title
        __typename
      }
      time_slot {
        id
        start_date
        start_time
        title
        multi_date
        __typename
      }
      promotion {
        id
        title
        __typename
      }
      upgrades {
        id
        product {
          id
          title
          is_ticket_fee
          __typename
        }
        product_variant {
          id
          title
          __typename
        }
        __typename
      }
      resale {
        id
        available
        total_amount
        fee
        public_url
        public_token
        __typename
      }
      __typename
    }
    __typename
  }
}
"""
}

headers = {
    "Content-Type" : "application/json"
}

print("Starting polling..")

while True:

    response = requests.post(GRAPHQL_URL, data=json.dumps(graph), headers=headers)

    assert response.status_code == 200

    payload = json.loads(response.content.decode('utf-8'))

    event = payload['data']['event']

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    assert type(event["registrations_for_sale_count"]) == type(event["filtered_registrations_for_sale_count"]) == int

    if event["registrations_for_sale_count"] > 0:
        webbrowser.open(URL, new=1, autoraise=True)
        print("!!! TICKET FOUND !!!")
        for _ in range(5): make_sound()
    elif event["filtered_registrations_for_sale_count"] > 0:
        make_sound()
        print("Reserved ticket found..")
    else:
        print(current_time, "No tickets..")

    time.sleep(15)
