# apartment_crawler

This is a web crawler designed to fetch rental apartment ads from vuokraovi.com portal. In addition to this, it also uses HSL api's to fetch public transit travel times to defined addresses from the address of the apartments in the ads.

A simple Flask app is implemented for demo purposes. There also exists functions to save the ads to a Mongo db, and to send the ads to a Slack channel via a webhook.
